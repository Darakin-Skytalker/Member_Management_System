/*
 * script.js: client-side behaviour shared by several pages.
 *
 * The same file is loaded on register.html, dashboard.html and admin.html.
 * Each section below targets one page. Elements that don't exist on the
 * current page come back as null, so most handlers are wrapped in an
 * "if (element)" check to avoid errors on the other pages.
 */

/*register.html*/
// Two-step registration: "Preview" shows a summary instead of submitting.
const previewBtn = document.getElementById("preview-btn");
const form = document.querySelector("form");   // the first <form> on the page
const previewSection = document.getElementById("preview-section");
const previewContent = document.getElementById("preview-content");
if (previewBtn) {
    previewBtn.addEventListener("click", function () {
        // Run the browser's built-in validation (required fields, email
        // format...). Stop here if something is missing or invalid.
        if (!form.reportValidity()) {
            return;
        }
        // Read the values the person typed
        const name = document.getElementById("name").value;
        const nationalId = document.getElementById("national_id").value;
        const phone = document.getElementById("Phone_NO").value;
        const address = document.getElementById("address").value;
        const birthDate = document.getElementById("Birth_Date").value;
        const sex = document.querySelector('input[name="sex"]:checked')?.value;
        const email = document.getElementById("email").value;

        // Build the summary shown in the preview section
        previewContent.innerHTML = `
        <p><strong>Name:</strong> ${name}</p>
        <p><strong>National ID:</strong> ${nationalId}</p>
        <p><strong>Phone:</strong> ${phone}</p>
        <p><strong>Address:</strong> ${address}</p>
        <p><strong>Birth Date:</strong> ${birthDate}</p>
        <p><strong>Sex:</strong> ${sex}</p>
        <p><strong>Email:</strong> ${email}</p>`;

        // Swap the form for the preview
        form.hidden = true;
        previewSection.hidden = false;

    });
}


// "Go Back and Edit": return from the preview to the form (entered values
// are kept because the form was only hidden, not reset).
const editBtn = document.getElementById("edit-btn");
if (editBtn) {
    editBtn.addEventListener("click", function () {
        previewSection.hidden = true;
        form.hidden = false;
    });
}
/*-----------------------------------------------------------*/


/*dashboard.html*/
// Opening the "Edit Information" or "Change Password" form hides the
// read-only info and the other buttons; Cancel puts everything back.
const editInfoBtn = document.getElementById("edit-info-btn");
const dashboardInfo = document.querySelector(".dashboard-info");
const editInfoSection = document.getElementById("edit-info-section");
const editInfoForm = document.getElementById("edit-info-form");
const passChngForm = document.getElementById("pass-change-form");
const passChngBtn = document.getElementById("pass-change-btn");
const passChngSection = document.getElementById("pass-change-section");
const adminDashBtn = document.getElementById("admin_dashboard_btn");  // admins only
const logoutBtn = document.getElementById("logout-btn");
if (editInfoBtn) {
    // Show the edit form and hide the rest
    editInfoBtn.addEventListener("click", function () {
        dashboardInfo.hidden = true;
        editInfoSection.hidden = false;
        editInfoBtn.hidden = true;
        passChngBtn.hidden = true;
        adminDashBtn.hidden = true;
        logoutBtn.hidden = true;
    });
}


const cancelEditBtn = document.getElementById("cancel-edit-btn");
if (cancelEditBtn) {
    // Discard any changes (reset the form) and restore the normal view
    cancelEditBtn.addEventListener("click", function () {
        editInfoForm.reset();
        editInfoSection.hidden = true;
        dashboardInfo.hidden = false;
        editInfoBtn.hidden = false;
        passChngBtn.hidden = false;
        adminDashBtn.hidden = false;
        logoutBtn.hidden = false;
    });
}


if (passChngBtn) {
    // Show the change-password form and hide the rest
    passChngBtn.addEventListener("click", function () {
        dashboardInfo.hidden = true;
        passChngSection.hidden = false;
        editInfoBtn.hidden = true;
        passChngBtn.hidden = true;
        adminDashBtn.hidden = true;
        logoutBtn.hidden = true;
    });
}

const cancelPassBtn = document.getElementById("cancel-pass-btn");
if (cancelPassBtn) {
    // Clear the typed passwords and restore the normal view
    cancelPassBtn.addEventListener("click", function () {
        passChngForm.reset();
        passChngSection.hidden = true;
        dashboardInfo.hidden = false;
        editInfoBtn.hidden = false;
        passChngBtn.hidden = false;
        adminDashBtn.hidden = false;
        logoutBtn.hidden = false;
    });
}
/*---------------------------------------------------------------*/


/*admin.html*/
// Clicking "Review" on an applicant card shows their details and copies
// their id into the Approve and Reject forms.
const approveApplicantId = document.getElementById("approve-applicant-id");
const rejectApplicantId = document.getElementById("reject-applicant-id");
const reviewButtons = document.querySelectorAll(".review-btn");
const reviewSection = document.getElementById("review-section");
const applicantDetails = document.getElementById("applicant-details");

let selectedApplicantId = null;   // id of the applicant currently under review
reviewButtons.forEach(function (button) {
    button.addEventListener("click", function () {
        // Remember the applicant and put the id in both hidden form fields
        const applicantId = button.dataset.id;
        selectedApplicantId = applicantId;
        approveApplicantId.value = applicantId;
        rejectApplicantId.value = applicantId;
        // The other details come from the button's data-* attributes
        const applicant = {
                name: button.dataset.name,
                email: button.dataset.email,
                phone: button.dataset.phone,
                address: button.dataset.address,
                national: button.dataset.national,
                birthdate: button.dataset.birthdate
            };
        // textContent (not innerHTML) so the values are shown as plain text
        applicantDetails.textContent =
            `Name: ${applicant.name} | Email: ${applicant.email}
            | Phone: ${applicant.phone} | Address: ${applicant.address}
            | National id: ${applicant.national} | Birth Date: ${applicant.birthdate}`;

        reviewSection.hidden = false;
    });
});



// "Close" hides the review panel without doing anything
const closeReviewBtn = document.getElementById("close-review-btn");
if (closeReviewBtn) {
    closeReviewBtn.addEventListener("click", function () {
        reviewSection.hidden = true;
    });
}
/* ----------------------------------------------------------*/


/* Browser back button auto reload
(so that no one get access to browser cache of
a pre-logged in page by clicking on the browser back button)*/
// event.persisted is true when the page was restored from the browser's
// back/forward cache instead of being loaded fresh from the server.
window.addEventListener("pageshow", function(event) {
    if (event.persisted) {
        window.location.reload();
    }
});
