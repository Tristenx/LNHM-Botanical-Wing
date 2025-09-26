#pylint: disable=invalid-name, unused-argument
"""Code for an AWS Lambda Function that will email parameters of plant emergency alerts. """
import os
import boto3

# Create SES client
ses = boto3.client('ses')

def lambda_handler(event, context):
    """Lambda handler for alert. """
    # Extract details from the event
    plant = event.get('plant', 'Unknown')
    emergency_type = event.get('emergency_type', 'Unknown')
    botanist = event.get('botanist', 'Unknown')
    phone = event.get('phone', 'Not provided')

    # email for both sender and recipient -
    EMAIL = os.environ.get("ALERT_EMAIL")

    SUBJECT = f"Plant At Risk Alert: {plant}"

    BODY_TEXT = (
        f"Hello {botanist},\n\n"
        f"The following plant has been flagged as at risk:\n\n"
        f"Plant: {plant}\n"
        f"Emergency Type: {emergency_type}\n"
        f"Contact: {phone}\n\n"
        f"Please take immediate action."
    )

    BODY_HTML = f"""<html>
    <body>
        <h2>Plant At Risk Alert</h2>
        <p>Hello <b>{botanist}</b>,</p>
        <p>The following plant has been flagged as at risk:</p>
        <ul>
            <li><b>Plant:</b> {plant}</li>
            <li><b>Emergency Type:</b> {emergency_type}</li>
            <li><b>Contact:</b> {phone}</li>
        </ul>
        <p>Please take immediate action.</p>
    </body>
    </html>
    """

    # Send the email using SES
    response = ses.send_email(
        Source=EMAIL,                 # Sender
        Destination={"ToAddresses": [EMAIL]},  # Recipient (same as sender)
        Message={
            "Subject": {"Data": SUBJECT},
            "Body": {
                "Text": {"Data": BODY_TEXT},
                "Html": {"Data": BODY_HTML}
            },
        },
    )

    return {
        "statusCode": 200,
        "body": f"Email sent to {EMAIL}. Message ID: {response['MessageId']}"
    }
