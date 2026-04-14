let allOrders = [];

async function fetchOrders() {
    try {
        const res = await fetch('api/orders');
        allOrders = await res.json();
        renderTable(allOrders);
        updateStats(allOrders);
    } catch (err) {
        console.error('Failed to fetch orders:', err);
    }
}

function renderTable(orders) {
    const body = document.getElementById('orders-body');
    body.innerHTML = '';

    if (orders.length === 0) {
        body.innerHTML = '<tr><td colspan="6" class="no-data">No orders yet. Click "New Order" to add one.</td></tr>';
        return;
    }

    orders.forEach((order, idx) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${idx + 1}</td>
            <td><span class="order-code-tag">${order.order_code}</span></td>
            <td>${order.first_name} ${order.last_name}</td>
            <td><span class="phone-masked">${maskPhone(order.phone)}</span></td>
            <td>${formatDate(order.created_at)}</td>
            <td>
                <button class="btn btn-danger btn-sm" onclick="deleteOrder(${order.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        body.appendChild(tr);
    });
}

function updateStats(orders) {
    document.getElementById('stat-total').innerText = orders.length;

    const uniquePhones = new Set(orders.map(o => o.phone));
    document.getElementById('stat-customers').innerText = uniquePhones.size;

    if (orders.length > 0) {
        document.getElementById('stat-latest').innerText = '#' + orders[0].order_code;
    } else {
        document.getElementById('stat-latest').innerText = '-';
    }
}

function maskPhone(phone) {
    if (!phone || phone.length < 7) return phone || '-';
    return phone.slice(0, 5) + '****' + phone.slice(-2);
}

function formatDate(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleString('en-US');
}

// Modal
function openModal() {
    document.getElementById('order-modal').classList.add('active');
    hideAlert();
}

function closeModal() {
    document.getElementById('order-modal').classList.remove('active');
    document.getElementById('order-form').reset();
    hideAlert();
}

function showAlert(msg, type) {
    const alert = document.getElementById('modal-alert');
    alert.textContent = msg;
    alert.className = 'alert ' + type;
    alert.style.display = 'block';
}

function hideAlert() {
    const alert = document.getElementById('modal-alert');
    alert.style.display = 'none';
}

async function submitOrder(e) {
    e.preventDefault();

    const data = {
        first_name: document.getElementById('first_name').value.trim(),
        last_name: document.getElementById('last_name').value.trim(),
        phone: document.getElementById('phone').value.trim(),
        order_code: document.getElementById('order_code').value.trim()
    };

    if (!/^\d{4}$/.test(data.order_code)) {
        showAlert('Order code must be exactly 4 digits.', 'error');
        return;
    }

    try {
        const res = await fetch('api/orders', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await res.json();

        if (res.ok) {
            closeModal();
            fetchOrders();
        } else {
            showAlert(result.error || 'Failed to create order.', 'error');
        }
    } catch (err) {
        showAlert('Network error. Please try again.', 'error');
    }
}

async function deleteOrder(id) {
    if (!confirm('Are you sure you want to delete this order?')) return;

    try {
        await fetch(`api/orders/${id}`, { method: 'DELETE' });
        fetchOrders();
    } catch (err) {
        console.error('Failed to delete order:', err);
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    window.onclick = function (event) {
        const modal = document.getElementById('order-modal');
        if (event.target === modal) {
            closeModal();
        }
    };

    fetchOrders();
    setInterval(fetchOrders, 20000);
});
