function showAlert(message, type) {
    const container = document.getElementById('alert-container');
    container.innerHTML = `
        <div class="alert alert-${type}">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
            ${message}
        </div>
    `;
    setTimeout(() => {
        container.innerHTML = '';
    }, 5000);
}

document.addEventListener('DOMContentLoaded', fetchCustomers);

async function fetchCustomers() {
    try {
        const response = await fetch('/api/customers');
        const data = await response.json();
        
        const tbody = document.getElementById('customers-body');
        tbody.innerHTML = '';
        
        data.forEach(customer => {
            const tr = document.createElement('tr');
            
            // Department Badge Magic
            let badgeClass = 'new';
            if (customer.department === 'Support') badgeClass = 'active';
            
            tr.innerHTML = `
                <td>${escapeHTML(customer.name)}</td>
                <td><span class="badge ${badgeClass}">${escapeHTML(customer.department)}</span></td>
                <td>${escapeHTML(customer.phone)}</td>
                <td>
                    <div class="actions-flex">
                        <button class="btn btn-primary" onclick="initiateCall('${escapeHTML(customer.phone)}', this)" title="Call via Hipcall">
                            <i class="fas fa-phone"></i> Call
                        </button>
                        <button class="btn btn-secondary" onclick="editCustomer(${customer.id}, '${escapeHTML(customer.name)}', '${escapeHTML(customer.department)}', '${escapeHTML(customer.phone)}')">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-danger" onclick="deleteCustomer(${customer.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
        
    } catch(err) {
        console.error(err);
        showAlert('Failed to load customers.', 'danger');
    }
}

// Security Helper
function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, 
        tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag] || tag)
    );
}

// Call Logic
async function initiateCall(phoneNumber, buttonElement) {
    const originalText = buttonElement.innerHTML;
    buttonElement.disabled = true;
    buttonElement.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

    try {
        const response = await fetch('/api/call', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ callee_number: phoneNumber })
        });

        const data = await response.json();

        if (response.ok) {
            showAlert('Call initiated! Your phone/app will ring first.', 'success');
            buttonElement.innerHTML = '<i class="fas fa-check"></i>';
            setTimeout(() => {
                buttonElement.innerHTML = originalText;
                buttonElement.disabled = false;
            }, 3000);
        } else {
            let errorMsg = data.error || 'Unknown error';
            if (data.hipcall_response && data.hipcall_response.errors && data.hipcall_response.errors.detail) {
                errorMsg += `: ${data.hipcall_response.errors.detail}`;
            } else if (data.hipcall_response && data.hipcall_response.message) {
                errorMsg += `: ${data.hipcall_response.message}`;
            }
            showAlert(`Failed: ${errorMsg}`, 'danger');
            buttonElement.innerHTML = originalText;
            buttonElement.disabled = false;
        }

    } catch (error) {
        console.error('Call failed', error);
        showAlert('Network error occurred while attempting to call.', 'danger');
        buttonElement.innerHTML = originalText;
        buttonElement.disabled = false;
    }
}


// --- CRUD MODAL LOGIC ---

function openModal() {
    document.getElementById('customer_id').value = '';
    document.getElementById('name').value = '';
    document.getElementById('phone').value = '';
    document.getElementById('modal-title').innerHTML = '<i class="fas fa-user-plus"></i> Add Customer';
    document.getElementById('customer-modal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('customer-modal').style.display = 'none';
}

function editCustomer(id, name, department, phone) {
    document.getElementById('customer_id').value = id;
    document.getElementById('name').value = name;
    document.getElementById('department').value = department;
    document.getElementById('phone').value = phone;
    document.getElementById('modal-title').innerHTML = '<i class="fas fa-edit"></i> Edit Customer';
    document.getElementById('customer-modal').style.display = 'flex';
}

async function submitCustomer(e) {
    e.preventDefault();
    const id = document.getElementById('customer_id').value;
    const name = document.getElementById('name').value;
    const department = document.getElementById('department').value;
    const phone = document.getElementById('phone').value;
    
    let method = id ? 'PUT' : 'POST';
    let url = id ? `/api/customers/${id}` : '/api/customers';
    
    try {
        const res = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, department, phone })
        });
        
        if (res.ok) {
            closeModal();
            showAlert('Customer saved successfully!', 'success');
            fetchCustomers();
        } else {
            const data = await res.json();
            showAlert(data.error || 'Failed to save customer', 'danger');
        }
    } catch(err) {
        console.error(err);
        showAlert('Network error', 'danger');
    }
}

async function deleteCustomer(id) {
    if(!confirm("Are you sure you want to delete this customer?")) return;
    try {
        const res = await fetch(`/api/customers/${id}`, { method: 'DELETE' });
        if(res.ok) {
            showAlert('Customer deleted', 'success');
            fetchCustomers();
        }
    } catch(err) {
        console.error(err);
        showAlert('Network error', 'danger');
    }
}
