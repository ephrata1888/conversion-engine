import resend
import os

resend.api_key = "re_aHaNHjxS_QJjtYAbv8rqx7HZEBw9rrgwt"

response = resend.Emails.send({
    "from": "onboarding@resend.dev",
    "to": "ephratawolde990@gmail.com",
    "subject": "Test from Conversion Engine",
    "html": "<p>Email pipeline is working.</p>"
})

print(response)