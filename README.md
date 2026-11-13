# Member Management System

A web-based member management system built with **Python, Flask, MySQL, HTML, CSS, and JavaScript**.

## Features

- **Member Registration:** Users can register and submit their information for approval.
- **Registration Review:** Administrators can review, approve, or reject applications.
- **Authentication:** Login and logout functionality with password hashing.
- **Member Dashboard:** Members can view and update their account information.
- **Password Management:** Members can change their passwords.
- **Member Directory:** Displays approved members.
- **Public Profiles:** Each approved member has a unique profile URL.
- **Profile Photos:** Supports uploading member profile pictures.
- **Role-Based Access:** Separate permissions for administrators and regular members.

## Technologies Used

- Python
- Flask
- MySQL
- HTML5
- CSS3
- JavaScript
- Werkzeug

## Database

The application uses **MySQL** for storing member information, account credentials, roles, and application statuses.

The database structure is provided in [`schema.sql`](schema.sql).

## Notes

- New registrations have a `pending` status until an administrator approves them.
- Only approved members can log in.
- Administrator access is restricted by user role.
- Public profiles are accessible through unique member URLs.
