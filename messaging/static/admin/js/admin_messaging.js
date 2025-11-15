// messaging/static/admin/js/admin_messaging.js - محدث وحقيقي

// ===== دوال جلب البيانات الحقيقية من APIs =====
function loadRealNotifications() {
    const notificationsList = document.getElementById('notificationsList');
    if (!notificationsList) return;

    notificationsList.innerHTML = '<div class="loading">جاري تحميل الإشعارات...</div>';

    // جلب الإشعارات الحقيقية من API
    fetch('/admins/get_admin_notifications/')
        .then(response => response.json())
        .then(data => {
            if (data.notifications && data.notifications.length > 0) {
                let notificationsHTML = '';
                data.notifications.forEach(notification => {
                    notificationsHTML += `
                        <div class="notification-item ${notification.is_read ? '' : 'unread'}">
                            <div class="notification-icon">${notification.icon || '📢'}</div>
                            <div class="notification-content">
                                <div class="notification-title">${notification.title}</div>
                                <div class="notification-preview">${notification.preview}</div>
                                <div class="notification-time">${notification.time}</div>
                            </div>
                        </div>
                    `;
                });
                notificationsList.innerHTML = notificationsHTML;
            } else {
                notificationsList.innerHTML = `
                    <div class="empty-state">
                        <div class="icon">🔔</div>
                        <p>لا توجد إشعارات</p>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error loading notifications:', error);
            notificationsList.innerHTML = `
                <div class="empty-state">
                    <div class="icon">⚠️</div>
                    <p>حدث خطأ في تحميل الإشعارات</p>
                </div>
            `;
        });
}

function loadRealMessages() {
    const messagesList = document.getElementById('messagesList');
    if (!messagesList) return;

    messagesList.innerHTML = '<div class="loading">جاري تحميل الرسائل...</div>';

    // جلب الرسائل الحقيقية من API
    fetch('/admins/get_admin_messages/')
        .then(response => response.json())
        .then(data => {
            if (data.messages && data.messages.length > 0) {
                let messagesHTML = '';
                data.messages.forEach(message => {
                    messagesHTML += `
                        <div class="message-item ${message.is_read ? '' : 'unread'}" onclick="markMessageAsRead(${message.id})">
                            <div class="message-icon">👤</div>
                            <div class="message-content">
                                <div class="message-title">${message.sender_name}</div>
                                <div class="message-preview">${message.preview}</div>
                                <div class="message-time">${message.time}</div>
                            </div>
                        </div>
                    `;
                });
                messagesList.innerHTML = messagesHTML;
            } else {
                messagesList.innerHTML = `
                    <div class="empty-state">
                        <div class="icon">✉️</div>
                        <p>لا توجد رسائل</p>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error loading messages:', error);
            messagesList.innerHTML = `
                <div class="empty-state">
                    <div class="icon">⚠️</div>
                    <p>حدث خطأ في تحميل الرسائل</p>
                </div>
            `;
        });
}

// ===== تحديث دوال base_site.html لاستخدام البيانات الحقيقية =====
function loadNotifications() {
    loadRealNotifications();
}

function loadMessages() {
    loadRealMessages();
}

// ===== دوال إضافية للتعامل مع الرسائل الحقيقية =====
function markMessageAsRead(messageId) {
    fetch(`/messaging/read/${messageId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // تحديث الواجهة
            const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
            if (messageElement) {
                messageElement.classList.remove('unread');
            }
            // تحديث العداد
            loadRealAdminUnreadCount();
        }
    })
    .catch(error => {
        console.error('Error marking message as read:', error);
    });
}

// ===== تحديث العداد الحقيقي =====
function loadRealAdminUnreadCount() {
    // جلب معرف المسؤول الحقيقي
    fetch('/admins/get_current_admin/')
        .then(response => response.json())
        .then(data => {
            const adminId = data.admin_id || 1;
            fetch(`/messaging/unread/admin/${adminId}/`)
                .then(response => response.json())
                .then(data => {
                    const badge = document.getElementById('adminNotificationBadge');
                    if (badge && data.unread_count > 0) {
                        badge.textContent = data.unread_count;
                        badge.style.display = 'flex';
                    } else if (badge) {
                        badge.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Error loading admin notifications:', error);
                });
        })
        .catch(error => {
            console.error('Error getting current admin:', error);
        });
}

// ===== تهيئة عند تحميل الصفحة =====
document.addEventListener('DOMContentLoaded', function() {
    // تحديث العداد لاستخدام الدالة الحقيقية
    loadRealAdminUnreadCount();
    
    // تحديث كل 30 ثانية
    setInterval(loadRealAdminUnreadCount, 30000);
});