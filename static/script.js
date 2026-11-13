/*register.html*/
const previewBtn = document.getElementById("preview-btn");
const form = document.querySelector("form");
const previewSection = document.getElementById("preview-section");
const previewContent = document.getElementById("preview-content");
if (previewBtn) {
    previewBtn.addEventListener("click", function () {
        if (!form.reportValidity()) {
            return;
        }    
        const name = document.getElementById("name").value;
        const nationalId = document.getElementById("national_id").value;
        const phone = document.getElementById("Phone_NO").value;
        const address = document.getElementById("address").value;
        const birthDate = document.getElementById("Birth_Date").value;
        const sex = document.querySelector('input[name="sex"]:checked')?.value;
        const email = document.getElementById("email").value;

        previewContent.innerHTML = `
        <p><strong>Name:</strong> ${name}</p>
        <p><strong>National ID:</strong> ${nationalId}</p>
        <p><strong>Phone:</strong> ${phone}</p>
        <p><strong>Address:</strong> ${address}</p>
        <p><strong>Birth Date:</strong> ${birthDate}</p>
        <p><strong>Sex:</strong> ${sex}</p>
        <p><strong>Email:</strong> ${email}</p>`;

        form.hidden = true;
        previewSection.hidden = false;

    });
}


const editBtn = document.getElementById("edit-btn");
if (editBtn) {
    editBtn.addEventListener("click", function () {
        previewSection.hidden = true;
        form.hidden = false;
    });
}
/*-----------------------------------------------------------*/


/*dashboard.html*/
const editInfoBtn = document.getElementById("edit-info-btn");
const dashboardInfo = document.querySelector(".dashboard-info");
const editInfoSection = document.getElementById("edit-info-section");
const editInfoForm = document.getElementById("edit-info-form");
const passChngForm = document.getElementById("pass-change-form");
const passChngBtn = document.getElementById("pass-change-btn");
const passChngSection = document.getElementById("pass-change-section");
const adminDashBtn = document.getElementById("admin_dashboard_btn");
const logoutBtn = document.getElementById("logout-btn");
if (editInfoBtn) {
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
const approveApplicantId = document.getElementById("approve-applicant-id");
const rejectApplicantId = document.getElementById("reject-applicant-id");
const reviewButtons = document.querySelectorAll(".review-btn");
const reviewSection = document.getElementById("review-section");
const applicantDetails = document.getElementById("applicant-details");

let selectedApplicantId = null;
reviewButtons.forEach(function (button) {
    button.addEventListener("click", function () {
        const applicantId = button.dataset.id;
        selectedApplicantId = applicantId;
        approveApplicantId.value = applicantId;
        rejectApplicantId.value = applicantId;  
        const applicant = {
                name: button.dataset.name,
                email: button.dataset.email,
                phone: button.dataset.phone,
                address: button.dataset.address,
                national: button.dataset.national,
                birthdate: button.dataset.birthdate
            };
        applicantDetails.textContent =
            `Name: ${applicant.name} | Email: ${applicant.email} 
            | Phone: ${applicant.phone} | Address: ${applicant.address}
            | National id: ${applicant.national} | Birth Date: ${applicant.birthdate}`;

        reviewSection.hidden = false;
    });
});



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
window.addEventListener("pageshow", function(event) {
    if (event.persisted) {
        window.location.reload();
    }
});