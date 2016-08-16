from mail_templated import send_mail

def send_submission_email(resource):
    send_mail('emails/submission_received.tpl', {},
              'info@openeducationweek.org', [resource.email]
    )
