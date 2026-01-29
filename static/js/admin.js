// Admin Panel JavaScript

document.addEventListener('DOMContentLoaded', function () {
    // Sidebar toggle for mobile
    const toggleBtn = document.querySelector('.toggle-sidebar');
    const sidebar = document.querySelector('.admin-sidebar');

    if (toggleBtn) {
        toggleBtn.addEventListener('click', function () {
            sidebar.classList.toggle('open');
        });
    }

    // Delete confirmation
    window.deletePost = function (postId) {
        if (confirm('Haqiqatan ham bu maqolani o\'chirmoqchimisiz?')) {
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/admin/posts/${postId}/delete`;
            document.body.appendChild(form);
            form.submit();
        }
    };

    // Select all checkbox
    const selectAll = document.querySelector('thead input[type="checkbox"]');
    if (selectAll) {
        selectAll.addEventListener('change', function () {
            document.querySelectorAll('tbody input[type="checkbox"]').forEach(cb => {
                cb.checked = this.checked;
            });
        });
    }

    // Search functionality
    const searchInput = document.querySelector('.header-search input');
    if (searchInput) {
        searchInput.addEventListener('input', function (e) {
            const query = e.target.value.toLowerCase();
            document.querySelectorAll('.admin-table tbody tr').forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            });
        });
    }

    // Close dropdowns when clicking outside
    document.addEventListener('click', function (e) {
        if (!e.target.closest('.notifications-dropdown')) {
            document.getElementById('notificationsMenu')?.classList.remove('show');
        }
        if (!e.target.closest('.user-dropdown')) {
            document.getElementById('userMenuDropdown')?.classList.remove('show');
        }
    });
});

// Toggle notifications dropdown
function toggleNotifications() {
    const menu = document.getElementById('notificationsMenu');
    const userMenu = document.getElementById('userMenuDropdown');

    userMenu?.classList.remove('show');
    menu?.classList.toggle('show');
}

// Toggle user menu dropdown
function toggleUserMenu() {
    const menu = document.getElementById('userMenuDropdown');
    const notifMenu = document.getElementById('notificationsMenu');

    notifMenu?.classList.remove('show');
    menu?.classList.toggle('show');
}
