#!/usr/bin/env python3
import re
import dns.resolver
import smtplib

def validate_email_format(email):
    """
    Validate the email format using a regular expression.
    """
    # This regex is a simple check and might not cover all valid emails.
    pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    if re.match(pattern, email):
        return True
    return False

def get_mx_record(domain):
    """
    Retrieve the MX record for the domain.
    Returns the hostname of the mail server with the highest priority.
    """
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        # Sort the MX records by priority (lowest preference number is highest priority)
        mx_records = sorted(answers, key=lambda r: r.preference)
        # Return the hostname (convert from dns.name.Name object to string)
        return str(mx_records[0].exchange).rstrip('.')  # remove trailing dot if any
    except Exception as e:
        print(f"Error retrieving MX record for domain '{domain}': {e}")
        return None

def check_email_deliverability(email):
    """
    Check whether an email address is deliverable by performing an SMTP handshake.
    """
    if not validate_email_format(email):
        print("The email address format is invalid.")
        return False

    # Extract the domain from the email address
    domain = email.split('@')[1]
    mx_host = get_mx_record(domain)
    if mx_host is None:
        print(f"Could not find MX records for domain '{domain}'. The email is likely undeliverable.")
        return False

    print(f"Connecting to mail server: {mx_host}")

    # SMTP conversation: connect to the mail server and simulate sending an email.
    try:
        # Establish an SMTP connection (port 25 is standard; some servers may require 587 or 465)
        server = smtplib.SMTP(timeout=10)
        server.connect(mx_host, 25)
        server.helo(server.local_hostname)  # Initiate handshake
        # Use a dummy sender address (this should be a valid email on your domain in a production setup)
        sender = "test@example.com"
        server.mail(sender)
        code, response = server.rcpt(email)
        server.quit()

        # SMTP reply code 250 or 251 generally means the server accepted the RCPT TO command.
        if code in (250, 251):
            print(f"The email address '{email}' appears to be deliverable (SMTP response code: {code}).")
            return True
        else:
            print(f"The email address '{email}' was rejected (SMTP response code: {code}).")
            return False

    except Exception as e:
        print(f"An error occurred during SMTP communication: {e}")
        return False

if __name__ == "__main__":
    email_to_check = input("Enter the email address to check: ").strip()
    check_email_deliverability(email_to_check)
