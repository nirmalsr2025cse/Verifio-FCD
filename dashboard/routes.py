from flask import Blueprint , render_template , session , redirect ,url_for , request , Response
from utils.db import Count, FCD_collection , Colleges , fs , Excel , excel_fs
from utils.extractor import extract_details , extract_text
from utils.excel import add_data_to_excel, create_empty_excel
from flask import send_file
import io
import os
from flask import jsonify
from datetime import date
import pytesseract

dashboard = Blueprint('dashboard',__name__)


@dashboard.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('auth.index'))
    email = session['user']
    user = Count.find_one({
        'email':email
    })

    if not user:
        main_user = FCD_collection.find_one({
            'email':email
        })
        if not main_user:
            return redirect(url_for('auth.index'))

        Count.insert_one({
            'FirstName':main_user['FirstName'],
            'LastName':main_user['LastName'],
            'email':main_user['email'],
            'projects_count':0,
            'projects':[]
        })

    user = Count.find_one({
        'email': email
    })
    project = sorted(
        user.get('projects', []),
        key=lambda x: x.get('created_at'),
        reverse=True
    )

    verified_count = 0
    fake_count = 0
    for p in project:
        verified_count+=p['verified_count']
        fake_count+=p['fake_count']
    return render_template('home.html' , projects=project , projects_count = user['projects_count'] , verified_count=verified_count,fake_count=fake_count)

@dashboard.route('/create_project_page', methods=["POST"])
def open_project_page():

    if 'user' not in session:
        return redirect(url_for('auth.index'))

    project_name = request.form.get("project")

    colleges = Colleges.find({}, {'college_name':1, 'location':1, '_id':0})
    college_list = [f"{c['college_name']} - {c['location']}" for c in colleges]

    return render_template(
        'create_project.html',
        project_name=project_name,
        colleges=college_list
    )

@dashboard.route('/check-project-name' , methods=["POST"])
def check_project_name():
    if 'user' not in session:
        return redirect(url_for('auth.index'))
    data = request.get_json()
    if not data:
        return jsonify({'exists':False})
    name = data.get('name')
    email = session['user']

    user = Count.find_one({
        'email':email
    })

    project = user.get('projects',[])

    for p in project:
        if p.get('project_name').lower() == name.lower():
            return jsonify({'exists':True})
    return jsonify({'exists':False})

@dashboard.route('/projects')
def projects():
    if 'user' not in session:
        return redirect(url_for('auth.index'))
    email = session['user']
    user = Count.find_one({
        'email':email
    })
    project = sorted(
        user.get('projects', []),
        key=lambda x: x.get('created_at'),
        reverse=True
    )
    return render_template('projects.html' , projects=project)


@dashboard.route('/create_project' , methods=["POST"])
def create_projects():
    if 'user' not in session:
        return redirect(url_for('auth.index'))
    name = request.form.get('project_name')

    if not name:
        return redirect(url_for('/home'))
    email = session['user']
    today = date.today().strftime("%Y-%m-%d")

    user = Count.find_one({
        'email':email
    })

    project = user.get('projects')

    colleges = Colleges.find({}, {'college_name': 1, 'location': 1, '_id': 0})

    college_names = [f"{c['college_name']} - {c['location']}" for c in colleges]

    for p in project:
        if p.get('project_name').lower() == name.lower():
            return render_template('create_project.html' , project_name = name , colleges = college_names)

    new_project = {
        'project_name': name,
        'certificates_count': 0,
        'verified_count': 0,
        'fake_count': 0,
        'created_at': today
    }
    Count.update_one(
        {'email': email},
        {
            '$push': {'projects': new_project},
            '$inc': {'projects_count': 1}
        }
    )

    create_empty_excel(email,name)

    return render_template('create_project.html' , colleges = college_names , project_name = name)

@dashboard.route('/verify' , methods=["POST"])
def verify():
    if 'user' not in session:
        return redirect(url_for('auth.index'))

    data = request.get_json()
    college = data.get('college')
    year = int(data.get('year'))
    name = data.get('name')
    cert_id = data.get('certId')
    project_name = data.get('project_name')


    email = session['user']
    clg_list = college.split('-')
    clg_name = clg_list[0].strip()

    doc = Colleges.find_one({
        "college_name": {"$regex": clg_name, "$options": "i"},
        "years": {
            "$elemMatch": {
                "year": year,
                "students": {
                    "$elemMatch": {
                        "name": {"$regex": name.strip(), "$options": "i"},
                        "certificate_id": cert_id
                    }
                }
            }
        }
    })

    if doc:
        Count.update_one(
            {"email": email, "projects.project_name": project_name},
            {
                "$inc": {
                    "projects.$.verified_count": 1,
                    "projects.$.certificates_count": 1
                }
            }
        )
        add_data_to_excel(email,project_name,data)
        return jsonify({"success": True})
    else:
        Count.update_one(
            {'email':email, "projects.project_name": project_name},
            {
                "$inc":{
                    "projects.$.fake_count":1,
                    "projects.$.certificates_count": 1
                }
            }
        )
        return jsonify({"success": False})

@dashboard.route('/verify_pdf', methods=["POST"])
def verify_pdf():
    if 'user' not in session:
        return redirect(url_for('auth.index'))

    file = request.files.get("file")
    project_name = request.form.get("project_name")

    if not file:
        return jsonify({"error": "No file uploaded"})

    if file.content_type != "application/pdf":
        return jsonify({"error": "Only PDF allowed"})

    file_path = "temp.pdf"
    file.save(file_path)

    try:
        text6,text11 = extract_text(file_path)

        details = extract_details(text6,text11)

        if not all(details.values()):
            return jsonify({
                "error": "Invalid certificate format",
                "details": details   # optional (for debug)
            })

        name = details["name"]
        cert_id = details["cert_id"]
        clg_name = details["college"]
        year = int(details["year"])

        doc = Colleges.find_one({
            "college_name": {"$regex": clg_name, "$options": "i"},
            "years": {
                "$elemMatch": {
                    "year": year,
                    "students": {
                        "$elemMatch": {
                            "name": {"$regex": name.strip(), "$options": "i"},
                            "certificate_id": cert_id
                        }
                    }
                }
            }
        })

        email = session['user']

        if doc:
            Count.update_one(
                {"email": email, "projects.project_name": project_name},
                {
                    "$inc": {
                        "projects.$.verified_count": 1,
                        "projects.$.certificates_count": 1
                    }
                }
            )
            add_data_to_excel(email,project_name,details)
            return jsonify({
                "success": True,
                "details": details
            })

        else:
            Count.update_one(
                {"email": email, "projects.project_name": project_name},
                {
                    "$inc": {
                        "projects.$.fake_count": 1,
                        "projects.$.certificates_count": 1
                    }
                }
            )

            return jsonify({
                "success": False,
                "details": details
            })

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@dashboard.route('/sheet')
def sheet():
    if 'user' not in session:
        return redirect(url_for('auth.index'))
    email = session['user']
    user = Count.find_one({
        'email':email,
    })

    project = sorted(
        user.get('projects', []),
        key=lambda x: x.get('created_at'),
        reverse=True
    )
    return render_template('sheet.html' , projects=project)

@dashboard.route('/download/<project_name>')
def download(project_name):

    if 'user' not in session:
        return redirect(url_for('auth.index'))

    email = session['user']

    record = Excel.find_one({
        "email": email,
        "project_name": project_name
    })

    if not record:
        return "File not found", 404

    file_data = excel_fs.get(record["excel_file_id"])

    return send_file(
        io.BytesIO(file_data.read()),
        download_name=f"{project_name}.xlsx",
        as_attachment=True
    )

@dashboard.route('/analytics')
def analytics():
    if 'user' not in session:
        return redirect(url_for('auth.index'))
    email = session['user']
    user = Count.find_one({
         'email':email
    })

    project = sorted(
        user.get('projects', []),
        key=lambda x: x.get('created_at'),
        reverse=True
    )
    total_verified = 0
    total_certificates = 0
    for p in project:
        total_verified+=p.get('verified_count',0)
        total_certificates+=p.get('certificates_count',0)
    accuracy = ((total_verified/total_certificates)*100 if total_certificates > 0 else 0)

    return render_template('analytics.html' , projects = project , projects_count = user['projects_count'] , accuracy = accuracy)

@dashboard.route('/verified')
def verified():
    if 'user' not in session:
        return redirect(url_for('auth.index'))
    email = session['user']
    user = Count.find_one({
        'email':email
    })

    project = sorted(
        user.get('projects', []),
        key=lambda x: x.get('created_at'),
        reverse=True
    )

    total_verified = 0

    for p in project:
        total_verified+=p['verified_count']

    return render_template('verified.html' , projects=project , total_verified=total_verified , plural = " Certificates are Verified" , singular = " Certificate is Verified" , zero = "No Verified Records")

@dashboard.route('/fake')
def fake():
    if 'user' not in session:
        return redirect(url_for('auth.index'))
    email = session['user']

    user = Count.find_one({
        'email':email
    })

    project = sorted(
        user.get('projects', []),
        key=lambda x: x.get('created_at'),
        reverse=True
    )

    total_fake = 0

    for p in project:
        total_fake+=p['fake_count']
    return render_template('fake.html' , projects=project , total_fake=total_fake , plural="Certificates are Fake" , singular="Certificate is Fake" , zero="No Verified records")

@dashboard.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('auth.index'))
    email = session['user']
    user1 = FCD_collection.find_one({
        'email':email
    })
    user2 = Count.find_one({
        'email':email
    })
    first_name = user1.get('FirstName')
    last_name = user1.get('LastName')
    userid = user1.get('_id')
    auth_type = user1.get('auth_type')
    created_at=user1.get('created_at')
    profile_image_id = user1.get('profile_image_id')
    projects_count = user2.get('projects_count')
    project = user2.get('projects',[])
    verified_count = 0
    fake_count = 0
    certificates_count = 0
    for p in project:
        certificates_count+=p.get('certificates_count')
        verified_count+=p.get('verified_count')
        fake_count+=p.get('fake_count')
    accuracy = round((verified_count/certificates_count)*100,2) if certificates_count > 0 else 0
    def gcd(num1 , num2):
        if num2==0:
            return num1
        return gcd(num2 , num1%num2)
    divisor = gcd(verified_count,fake_count)
    if divisor != 0:
        verified_ratio = verified_count // divisor
        fake_ratio = fake_count // divisor
        ratio = f"{verified_ratio}:{fake_ratio}"
    else:
        ratio = f"{verified_count}:{fake_count}"
    return render_template('profile.html',First_Name=first_name,Last_Name=last_name,Email=email,ID=userid,Auth_Type=auth_type,Date=created_at,projects=projects_count,Certificates=certificates_count,Accuracy=accuracy,Verified=verified_count,Fake=fake_count,Ratio=ratio,profile_image_id=profile_image_id)

@dashboard.route('/upload_profile_photo', methods=['POST'])
def upload_profile():
    if 'user' not in session:
        return redirect(url_for('auth.index'))

    email = session['user']
    user = FCD_collection.find_one({
        'email':email
    })

    from bson import ObjectId

    old_image_id = user.get('profile_image_id')

    if old_image_id:
        try:
            fs.delete(ObjectId(old_image_id))
        except:
            pass

    file = request.files['image']

    file_id = fs.put(
        file.read(),
        filename = email,
        content_type = file.content_type
    )

    FCD_collection.update_one(
        {'email': email},
        {'$set': {'profile_image_id': file_id}}
    )

    return "OK"

@dashboard.route('/get_profile_image/<file_id>')
def get_profile_image(file_id):
    from bson import ObjectId

    file = fs.get(ObjectId(file_id))

    return Response(file.read(),mimetype=file.content_type)

@dashboard.route('/delete_profile_photo', methods=['POST'])
def delete_profile_photo():
    if 'user' not in session:
        return redirect(url_for('auth.index'))

    email = session['user']
    user = FCD_collection.find_one({'email': email})

    file_id = user.get('profile_image_id')

    if file_id:
        from bson import ObjectId
        fs.delete(ObjectId(file_id))

    FCD_collection.update_one(
        {'email': email},
        {'$unset': {'profile_image_id': ""}}
    )

    return "OK"

@dashboard.route('/delete_project', methods=["POST"])
def delete_project():

    if 'user' not in session:
        return jsonify({"success": False})

    data = request.get_json()
    project_name = data.get("project_name")
    email = session['user']

    record = Excel.find_one({
        "email": email,
        "project_name": project_name
    })

    if record:
        excel_fs.delete(record["excel_file_id"])
        Excel.delete_one({"_id": record["_id"]})

    Count.update_one(
        {"email": email},
        {
            "$pull": {"projects": {"project_name": project_name}},
            "$inc": {"projects_count": -1}
        }
    )

    return jsonify({"success": True})

@dashboard.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.index'))