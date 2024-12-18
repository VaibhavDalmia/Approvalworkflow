from flask import Flask, request, redirect, flash, render_template_string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.secret_key = "a8acada22418a9128a35361b1fe528ee"  # Replace with a secure secret key

# Email Settings
SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "srivastava.vaibha@dalmiabharat.com"  # Replace with your email
APP_PASSWORD = "vylwscmnzwtvqhhf"  # Replace with your App Password

# Hosted URL of your application
HOSTED_URL = "https://approvalworkflow.onrender.com"  # Replace with your Render URL


class ApprovalForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    job = StringField("Job", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    phone_number = StringField("Phone Number", validators=[DataRequired()])
    submit = SubmitField("Submit for Approval")


@app.route("/", methods=["GET", "POST"])
def approval_form():
    form = ApprovalForm()
    if form.validate_on_submit():
        name = form.name.data
        job = form.job.data
        location = form.location.data
        phone_number = form.phone_number.data

        # Prepare the email content
        subject = f"Approval Request for {name}"
        body = f"""
        <html>
        <body>
            <h3>A new approval request has been submitted:</h3>
            <ul>
                <li><strong>Name:</strong> {name}</li>
                <li><strong>Job:</strong> {job}</li>
                <li><strong>Location:</strong> {location}</li>
                <li><strong>Phone Number:</strong> {phone_number}</li>
            </ul>
            <p>Please review the request using the button below:</p>
            <a href="{HOSTED_URL}/review?name={name}&job={job}&location={location}&phone_number={phone_number}" 
               style="padding:10px 15px; background-color: #28a745; color: white; text-decoration: none; border-radius: 5px;">Review</a>
            <br><br>
            <p>Alternatively, you can directly approve or reject:</p>
            <a href="{HOSTED_URL}/approve?name={name}" 
               style="padding:10px 15px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px;">Approve</a>
            <a href="{HOSTED_URL}/reject?name={name}" 
               style="padding:10px 15px; background-color: #dc3545; color: white; text-decoration: none; border-radius: 5px;">Reject</a>
        </body>
        </html>
        """

        try:
            # Send email
            msg = MIMEMultipart()
            msg["From"] = EMAIL_ADDRESS
            msg["To"] = "approver_email@domain.com"  # Replace with approver's email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "html"))  # Send email as HTML

            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(EMAIL_ADDRESS, APP_PASSWORD)
            server.send_message(msg)
            server.quit()

            flash("Approval request sent successfully!", "success")
        except Exception as e:
            flash(f"Error sending email: {e}", "danger")

        return redirect("/")

    # Render the form in the root page
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Approval Workflow</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 50px;
            }
            .form-container {
                width: 50%;
                margin: auto;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 5px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            label {
                display: block;
                margin-top: 10px;
                font-weight: bold;
            }
            input {
                width: 100%;
                padding: 10px;
                margin-top: 5px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            button {
                margin-top: 20px;
                padding: 10px 15px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
            button:hover {
                background-color: #0056b3;
            }
        </style>
    </head>
    <body>
        <div class="form-container">
            <h2>Approval Request Form</h2>
            <form method="post">
                {{ form.hidden_tag() }}
                <label for="name">Name:</label>
                {{ form.name() }}
                <label for="job">Job:</label>
                {{ form.job() }}
                <label for="location">Location:</label>
                {{ form.location() }}
                <label for="phone_number">Phone Number:</label>
                {{ form.phone_number() }}
                {{ form.submit(class_="btn btn-primary") }}
            </form>
        </div>
    </body>
    </html>
    """, form=form)


@app.route("/review")
def review():
    name = request.args.get("name")
    job = request.args.get("job")
    location = request.args.get("location")
    phone_number = request.args.get("phone_number")
    return f"""
    <h2>Review Request</h2>
    <p><strong>Name:</strong> {name}</p>
    <p><strong>Job:</strong> {job}</p>
    <p><strong>Location:</strong> {location}</p>
    <p><strong>Phone Number:</strong> {phone_number}</p>
    """


@app.route("/approve")
def approve():
    name = request.args.get("name")
    return f"<h2>Request Approved for {name}</h2>"


@app.route("/reject")
def reject():
    name = request.args.get("name")
    return f"<h2>Request Rejected for {name}</h2>"


if __name__ == "__main__":
    app.run(debug=True)
