import smtplib
import os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


def send_otp_email(to_email, otp):
    sender_email = os.getenv("EMAIL_USER")
    app_password = os.getenv("EMAIL_PASS")

    msg = MIMEMultipart("related")
    msg["Subject"] = "Password Reset Verification - Verifio"
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Reply-To"] = sender_email

    html_body = f"""
    <html>
    <body style="margin:0;padding:0;background:#ffffff;font-family:Arial,Helvetica,sans-serif;">

    <table width="100%" cellpadding="0" cellspacing="0" style="background:#ffffff;">
    <tr>
    <td align="center">

    <table width="620" cellpadding="0" cellspacing="0"
    style="background:#ffffff;border:1px solid #e5e5e5;border-radius:8px;">

        <tr>
            <td align="center" style="padding:30px 20px 10px 20px;">
                <img src="cid:logo_image" width="90">
            </td>
        </tr>

        <tr>
            <td align="center"
            style="font-size:34px;font-weight:bold;color:#1a73e8;padding-bottom:10px;">
                Verifio
            </td>
        </tr>

        <tr>
            <td align="center"
            style="font-size:30px;color:#222;padding:10px 30px;">
                Password Reset Verification
            </td>
        </tr>

        <tr>
            <td style="padding:0 35px;">
                <hr style="border:none;border-top:1px solid #dddddd;">
            </td>
        </tr>

        <tr>
            <td style="padding:30px 40px 10px 40px;
            font-size:18px;color:#333;line-height:30px;">

                Hello User,<br><br>

                We received a request to change your account password.
                To continue securely, please verify this request using the OTP below.

                <br><br>

                Use this One-Time Password to proceed:
            </td>
        </tr>

        <tr>
            <td align="center" style="padding:20px;">
                <div style="
                    display:inline-block;
                    background:#f8f9fa;
                    border:1px solid #dcdcdc;
                    border-radius:8px;
                    padding:22px 65px;
                    font-size:52px;
                    font-weight:bold;
                    letter-spacing:8px;
                    color:#111111;">
                    {otp}
                </div>
            </td>
        </tr>

        <tr>
            <td style="padding:20px 40px;
            font-size:17px;color:#444;line-height:28px;">

                <b>Important Information:</b><br><br>

                • This OTP is valid for 3 minutes only.<br>
                • Do not share this code with anyone.<br>
                • If you did not request a password change, ignore this email immediately.<br>
                • Your current password remains unchanged until verification is completed.

            </td>
        </tr>

        <tr>
            <td style="padding:10px 40px 30px 40px;
            font-size:17px;color:#444;line-height:28px;">

                Need help? Contact our support team anytime.

                <br><br>

                Regards,<br>
                <b>Team Verifio</b>
            </td>
        </tr>

        <tr>
            <td align="center"
            style="padding:20px;background:#ffffff;
            font-size:14px;color:#777777;border-top:1px solid #eeeeee;">

                © 2026 Verifio. All rights reserved.
            </td>
        </tr>

    </table>

    </td>
    </tr>
    </table>

    </body>
    </html>
    """

    msg.attach(MIMEText(html_body, "html"))

    with open("static/images/logo.png", "rb") as f:
        img = MIMEImage(f.read())

    img.add_header("Content-ID", "<logo_image>")
    img.add_header("Content-Disposition", "inline", filename="logo.png")
    msg.attach(img)

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()
        return True

    except Exception as e:
        print("Error:", e)
        return False