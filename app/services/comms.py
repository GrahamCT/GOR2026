import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_dotenv() 

def SendMail(to_email, subject ):
    api_key = os.getenv("SENDGRID_API_KEY")

    body = "Thank you for chosing to dine with us, your dining voucher for spur is attached."


    message = Mail(
        from_email ='graham@indigoio.co.za',
        to_emails=to_email,
        subject="Dinig Voucher - Graham Russon",
        html_content=body
    )


    sg = SendGridAPIClient(api_key)


    response = sg.send(message)

    print (response)


def send_email_template(to_email, subject, template_data, template_id):

    api_key = os.getenv("SENDGRID_API_KEY")

    # optionally inject subject into template data
    if subject:
        template_data["subject"] = subject

    message = Mail(
        from_email="graham@indigoio.co.za",
        to_emails=to_email
    )

    message.template_id = template_id
    message.dynamic_template_data = template_data

    try:
        sendgrid_client = SendGridAPIClient(api_key)
        response = sendgrid_client.send(message)

        print("Status:", response.status_code)
        print("Body:", response.body)
        print("Headers:", response.headers)

        return response.status_code

    except Exception as e:
        print("SendGrid error:", str(e))
        return None    



