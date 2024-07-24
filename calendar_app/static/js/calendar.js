// Initialize activities from window or set as an empty object if not present
const activities = window.activities || {};
console.log(activities);

let currentMonth = new Date().getMonth();  // Get current month
let currentYear = new Date().getFullYear();  // Get current year

// Render calendar on DOM content loaded
document.addEventListener('DOMContentLoaded', function () {
    renderCalendar(currentMonth, currentYear);
});

// Change month in calendar
function changeMonth(offset) {
    currentMonth += offset;
    if (currentMonth < 0) {
        currentMonth = 11;
        currentYear--;
    } else if (currentMonth > 11) {
        currentMonth = 0;
        currentYear++;
    }
    renderCalendar(currentMonth, currentYear);  // Re-render calendar with updated month/year
}

// Render calendar for the specified month and year
function renderCalendar(month, year) {
    const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    document.getElementById('current-month').textContent = `${monthNames[month]} ${year}`;

    const firstDay = new Date(year, month, 1).getDay();  // Day of the week for the first day of the month
    const daysInMonth = new Date(year, month + 1, 0).getDate();  // Total days in the month

    let calendarBody = document.getElementById('calendar-days');
    calendarBody.innerHTML = '';  // Clear previous calendar content

    let date = 1;
    for (let i = 0; i < 6; i++) {  // Loop through weeks
        let row = document.createElement('tr');

        for (let j = 0; j < 7; j++) {  // Loop through days of the week
            let cell = document.createElement('td');
            cell.className = 'calendar-cell';
            if (i === 0 && j < firstDay) {
                cell.innerHTML = '';  // Empty cells before the first day of the month
            } else if (date > daysInMonth) {
                break;  // Stop if past the last day of the month
            } else {
                const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(date).padStart(2, '0')}`;
                cell.innerHTML = date;
                if (activities[dateStr]) {
                    cell.classList.add('has-activity');  // Mark cell if there are activities
                    const redDot = document.createElement('div');
                    redDot.classList.add('red-dot');
                    cell.appendChild(redDot);
                }
                cell.addEventListener('click', () => showActivityDetails(dateStr));
                date++;
            }
            row.appendChild(cell);
        }
        calendarBody.appendChild(row);
    }
}

// Show the form to add an activity for a specific date
function showAddActivityForm(date) {
    document.getElementById('id_date').value = date;  // Set the date in the form
    document.getElementById('addActivityModal').style.display = 'block';  // Display the form
}

// Close the form to add an activity
function closeAddActivityForm() {
    document.getElementById('addActivityModal').style.display = 'none';  // Hide the form
}

// Show details of activities for a specific date
function showActivityDetails(date) {
    const activityDetails = document.getElementById('activity-details');
    const selectedDateElement = document.getElementById('selected-date');
    
    activityDetails.innerHTML = '';  // Clear previous details
    selectedDateElement.textContent = `${date}`;  // Update the date heading
    
    // Check if there are activities for the given date
    if (activities[date] && activities[date].length > 0) {
        activities[date].forEach(activity => {
            let activityElement = document.createElement('div');
            activityElement.innerHTML = `
                <div class="activity-title">${activity.title}</div>
                <div class="activity-description">${activity.description}</div>
                <br>`;
            activityDetails.appendChild(activityElement);
        });
    } else {
        activityDetails.innerHTML = '<p>No activities for this date.</p>';
    }
}

// Handle form submission for adding an activity
document.getElementById('activityForm').addEventListener('submit', function(event) {
    event.preventDefault();  // Prevent default form submission

    const dateField = document.getElementById('id_date');
    const selectedDate = new Date(dateField.value);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (selectedDate < today) {
        alert("The date cannot be in the past.");
        return;
    }

    const formData = new FormData(this);

    fetch(addActivityUrl, {  // Use the URL set by Django template
        method: 'POST',
        headers: {
            'X-CSRFToken': formData.get('csrfmiddlewaretoken'),  // CSRF token for security
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            closeAddActivityForm();  // Close the form on success
            location.reload();  // Reload the page to update the calendar
        } else {
            console.error('Error:', data.errors || 'An error occurred');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error adding activity');
    });
});
