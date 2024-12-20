from flask import Flask, render_template_string, request, redirect, flash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = "a8acada22418a9128a35361b1fe528ee"  # Secure key

# Email Settings
SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "srivastava.vaibha@dalmiabharat.com"  # Your Outlook email
APP_PASSWORD = "vylwscmnzwtvqhhf"  # Your App Password

# Hosted URL
HOSTED_URL = "https://approvalworkflow.onrender.com"  # Replace with your hosted URL

# Approval Tracking (for demonstration; replace with a database in production)
approval_status = {}
approval_data = {}  # To store the details of submitted requests

# HTML Templates
form_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Approval Form</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .form-container {
            background: #ffffff;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            max-width: 450px;
            width: 100%;
        }
        h2 {
            text-align: center;
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }
        input {
            width: 100%;
            padding: 10px;
            margin-bottom: 15px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        button {
            width: 100%;
            padding: 10px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #0056b3;
        }
        .flash {
            text-align: center;
            margin-bottom: 10px;
            padding: 10px;
            color: white;
            border-radius: 4px;
        }
        .success { background-color: #28a745; }
        .danger { background-color: #dc3545; }
    </style>
</head>
<body>
    <div class="form-container">
        <h2>Approval Form</h2>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="flash {{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        <form method="POST">
            <label for="name">Name:</label>
            <input type="text" name="name" id="name" required>

            <label for="phone_number">Phone Number:</label>
            <input type="text" name="phone_number" id="phone_number" required>

            <label for="address">Address:</label>
            <input type="text" name="address" id="address" required>

            <label for="gstin">GSTIN:</label>
            <input type="text" name="gstin" id="gstin" required>

            <label for="pan">PAN:</label>
            <input type="text" name="pan" id="pan" required>

            <label for="account_number">Bank Account Number:</label>
            <input type="text" name="account_number" id="account_number" required>

            <label for="ifsc_code">IFSC Code:</label>
            <input type="text" name="ifsc_code" id="ifsc_code" required>

            <button type="submit">Submit for Approval</button>
        </form>
    </div>
</body>
</html>
"""

email_template = """
<html>
<body>
    <p>A new approval request has been submitted:</p>
    <ul>
        <li><strong>Name:</strong> {name}</li>
        <li><strong>Phone Number:</strong> {phone_number}</li>
        <li><strong>Address:</strong> {address}</li>
        <li><strong>GSTIN:</strong> {gstin}</li>
        <li><strong>PAN:</strong> {pan}</li>
        <li><strong>Bank Account Number:</strong> {account_number}</li>
        <li><strong>IFSC Code:</strong> {ifsc_code}</li>
    </ul>
    <p>Click one of the buttons below to take action:</p>
    <a href="{hosted_url}/approve/{id}" style="text-decoration:none">
        <button style="background-color:green;color:white;padding:10px 15px;border:none;border-radius:5px;">Approve</button>
    </a>
    <a href="{hosted_url}/reject/{id}" style="text-decoration:none">
        <button style="background-color:red;color:white;padding:10px 15px;border:none;border-radius:5px;">Reject</button>
    </a>
    <a href="{hosted_url}/review/{id}" style="text-decoration:none">
        <button style="background-color:blue;color:white;padding:10px 15px;border:none;border-radius:5px;">Review</button>
    </a>
</body>
</html>
"""

review_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Review Request</title>
</head>
<body>
    <h2>Approval Request Details</h2>
    <ul>
        <li><strong>Name:</strong> {{ name }}</li>
        <li><strong>Phone Number:</strong> {{ phone_number }}</li>
        <li><strong>Address:</strong> {{ address }}</li>
        <li><strong>GSTIN:</strong> {{ gstin }}</li>
        <li><strong>PAN:</strong> {{ pan }}</li>
        <li><strong>Bank Account Number:</strong> {{ account_number }}</li>
        <li><strong>IFSC Code:</strong> {{ ifsc_code }}</li>
    </ul>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def approval_form():
    if request.method == "POST":
        # Extract form data
        name = request.form["name"]
        phone_number = request.form["phone_number"]
        address = request.form["address"]
        gstin = request.form["gstin"]
        pan = request.form["pan"]
        account_number = request.form["account_number"]
        ifsc_code = request.form["ifsc_code"]

        # Generate a unique ID for the request
        request_id = f"{name}-{phone_number}"
        approval_status[request_id] = "Pending"
        approval_data[request_id] = {
            "name": name,
            "phone_number": phone_number,
            "address": address,
            "gstin": gstin,
            "pan": pan,
            "account_number": account_number,
            "ifsc_code": ifsc_code
        }

        # Prepare the email content
        subject = f"Approval Request for {name}"
        body = email_template.format(
            name=name, phone_number=phone_number, address=address, gstin=gstin,
            pan=pan, account_number=account_number, ifsc_code=ifsc_code,
            id=request_id, hosted_url=HOSTED_URL
        )

        try:
            # Send email
            msg = MIMEMultipart("alternative")
            msg["From"] = EMAIL_ADDRESS
            msg["To"] = "das.rajesh@dalmiabharat.com"  # Replace with the approver's email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "html"))

            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(EMAIL_ADDRESS, APP_PASSWORD)
            server.send_message(msg)
            server.quit()

            flash("Approval request sent successfully!", "success")
        except Exception as e:
            flash(f"Error sending email: {e}", "danger")

        return redirect("/")
    return render_template_string(form_template)


@app.route("/review/<request_id>")
def review(request_id):
    if request_id in approval_data:
        data = approval_data[request_id]
        return render_template_string(review_template, **data)
    else:
        flash("Invalid review request.", "danger")
        return redirect("/")


@app.route("/approve/<request_id>")
def approve(request_id):
    if request_id in approval_status:
        approval_status[request_id] = "Approved"
        flash(f"Request {request_id} has been approved.", "success")
    else:
        flash("Invalid approval request.", "danger")
    return redirect("/")


@app.route("/reject/<request_id>")
def reject(request_id):
    if request_id in approval_status:
        approval_status[request_id] = "Rejected"
        flash(f"Request {request_id} has been rejected.", "danger")
    else:
        flash("Invalid rejection request.", "danger")
    return redirect("/")


if __name__ == "__main__":
    app.run(port=5003, debug=True)
