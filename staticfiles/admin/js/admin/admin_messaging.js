// static/admin/js/admin_messaging.js
document.addEventListener('DOMContentLoaded', function() {
    // إضافة أنماط CSS ديناميكياً
    const styles = `
        .admin-messaging-modal {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            width: 500px;
            max-width: 90vw;
            z-index: 10000;
            border: 1px solid #e2e8f0;
            overflow: hidden;
        }
        .admin-modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 9999;
        }
        .admin-modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            border-bottom: 1px solid #e2e8f0;
            background: #f8fafc;
        }
        .admin-modal-header h3 {
            margin: 0;
            color: #2d3748;
            font-size: 18px;
            font-weight: 600;
        }
        .admin-close-btn {
            background: none;
            border: none;
            font-size: 20px;
            cursor: pointer;
            padding: 5px;
            color: #718096;
        }
        .admin-modal-content {
            padding: 20px;
        }
        .admin-form-group {
            margin-bottom: 20px;
        }
        .admin-form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #4a5568;
            font-size: 14px;
        }
        .admin-form-input, .admin-form-textarea {
            width: 100%;
            padding: 12px;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            font-size: 14px;
            transition: all 0.3s ease;
        }
        .admin-form-input:focus, .admin-form-textarea:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            outline: none;
        }
        .admin-form-textarea {
            resize: vertical;
            min-height: 120px;
            font-family: inherit;
        }
        .admin-send-btn {
            width: 100%;
            background: #667eea;
            color: white;
            border: none;
            padding: 14px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .admin-send-btn:hover {
            background: #5a67d8;
            transform: translateY(-1px);
        }
        .quick-message-buttons {
            display: flex;
            gap: 10px;
            margin-top: 10px;
            flex-wrap: wrap;
        }
        .quick-message-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.3s ease;
        }
        .quick-message-btn:hover {
            background: #5a67d8;
        }
        .messages-list {
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 10px;
        }
        .message-item {
            padding: 12px;
            border-bottom: 1px solid #f0f0f0;
            margin-bottom: 8px;
            border-radius: 6px;
            background: #f8f9fa;
        }
        .message-item:last-child {
            border-bottom: none;
            margin-bottom: 0;
        }
        .message-item.unread {
            background: #e3f2fd;
            border-right: 3px solid #2196F3;
        }
        .message-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
        }
        .message-title {
            font-weight: 600;
            color: #2d3748;
        }
        .message-time {
            color: #718096;
            font-size: 12px;
        }
        .message-content {
            color: #4a5568;
            line-height: 1.4;
        }
        .empty-messages {
            text-align: center;
            padding: 40px;
            color: #718096;
        }
    `;
    
    const styleSheet = document.createElement('style');
    styleSheet.textContent = styles;
    document.head.appendChild(styleSheet);
});

// دالة إنشاء نافذة مراسلة سريعة للطالب
function sendQuickMessage(studentId) {
    createAdminModalOverlay();
    
    const modalHTML = `
        <div class="admin-messaging-modal">
            <div class="admin-modal-header">
                <h3>مراسلة سريعة - طالب</h3>
                <button class="admin-close-btn" onclick="closeAdminModals()">✕</button>
            </div>
            <div class="admin-modal-content">
                <div class="admin-form-group">
                    <label>عنوان الرسالة:</label>
                    <input type="text" id="quick-message-title" class="admin-form-input" placeholder="عنوان الرسالة">
                </div>
                <div class="admin-form-group">
                    <label>محتوى الرسالة:</label>
                    <textarea id="quick-message-content" class="admin-form-textarea" placeholder="اكتب محتوى الرسالة هنا..." rows="4"></textarea>
                </div>
                
                <div class="quick-message-buttons">
                    <button class="quick-message-btn" onclick="fillQuickMessage('ترحيب')">رسالة ترحيب</button>
                    <button class="quick-message-btn" onclick="fillQuickMessage('تنبيه')">رسالة تنبيه</button>
                    <button class="quick-message-btn" onclick="fillQuickMessage('إشعار')">إشعار مهم</button>
                </div>
                
                <button class="admin-send-btn" onclick="submitQuickMessage(${studentId})" style="margin-top: 20px;">إرسال الرسالة</button>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

// دالة عرض رسائل الطالب
function viewStudentMessages(studentId) {
    createAdminModalOverlay();
    
    const modalHTML = `
        <div class="admin-messaging-modal" style="width: 600px;">
            <div class="admin-modal-header">
                <h3>رسائل الطالب</h3>
                <button class="admin-close-btn" onclick="closeAdminModals()">✕</button>
            </div>
            <div class="admin-modal-content">
                <div class="messages-list" id="studentMessagesList">
                    <div style="text-align: center; padding: 20px; color: #718096;">جاري تحميل الرسائل...</div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    loadStudentMessages(studentId);
}

// دالة مراسلة المعلم
function sendMessageToTeacher(teacherId) {
    createAdminModalOverlay();
    
    const modalHTML = `
        <div class="admin-messaging-modal">
            <div class="admin-modal-header">
                <h3>مراسلة المعلم</h3>
                <button class="admin-close-btn" onclick="closeAdminModals()">✕</button>
            </div>
            <div class="admin-modal-content">
                <div class="admin-form-group">
                    <label>عنوان الرسالة:</label>
                    <input type="text" id="teacher-message-title" class="admin-form-input" placeholder="عنوان الرسالة">
                </div>
                <div class="admin-form-group">
                    <label>محتوى الرسالة:</label>
                    <textarea id="teacher-message-content" class="admin-form-textarea" placeholder="اكتب محتوى الرسالة هنا..." rows="4"></textarea>
                </div>
                <button class="admin-send-btn" onclick="submitTeacherMessage(${teacherId})">إرسال الرسالة</button>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

// دوال مساعدة
function createAdminModalOverlay() {
    closeAdminModals();
    const overlay = document.createElement('div');
    overlay.className = 'admin-modal-overlay';
    overlay.onclick = closeAdminModals;
    document.body.appendChild(overlay);
}

function closeAdminModals() {
    document.querySelectorAll('.admin-messaging-modal, .admin-modal-overlay').forEach(el => {
        el.remove();
    });
}

function fillQuickMessage(type) {
    const titleInput = document.getElementById('quick-message-title');
    const contentInput = document.getElementById('quick-message-content');
    
    const messages = {
        'ترحيب': {
            title: 'مرحباً بك في منصة التعليم الذكي',
            content: 'نرحب بك في منصتنا التعليمية ونتمنى لك تجربة تعليمية ممتعة ومفيدة. نحن هنا لمساعدتك في رحلتك التعليمية.'
        },
        'تنبيه': {
            title: 'تنبيه مهم',
            content: 'نود تذكيرك بموعد الامتحان القادم. يرجى مراجعة المواد الدراسية والاستعداد الجيد.'
        },
        'إشعار': {
            title: 'إشعار هام',
            content: 'تم تحديث المحتوى التعليمي للكورس. يرجى مراجعة الدروس الجديدة والمشاركة في الأنشطة.'
        }
    };
    
    if (messages[type]) {
        titleInput.value = messages[type].title;
        contentInput.value = messages[type].content;
    }
}

function submitQuickMessage(studentId) {
    const title = document.getElementById('quick-message-title').value;
    const content = document.getElementById('quick-message-content').value;
    
    if (!title || !content) {
        alert('يرجى ملء جميع الحقول');
        return;
    }
    
    const messageData = {
        receiver_type: 'student',
        receiver_id: studentId,
        title: title,
        content: content,
        sender_type: 'admin',
        sender_id: 1
    };
    
    fetch('/messaging/send/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(messageData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('تم إرسال الرسالة بنجاح');
            closeAdminModals();
        } else {
            alert('حدث خطأ في الإرسال: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('حدث خطأ في الإرسال');
    });
}

function submitTeacherMessage(teacherId) {
    const title = document.getElementById('teacher-message-title').value;
    const content = document.getElementById('teacher-message-content').value;
    
    if (!title || !content) {
        alert('يرجى ملء جميع الحقول');
        return;
    }
    
    const messageData = {
        receiver_type: 'teacher',
        receiver_id: teacherId,
        title: title,
        content: content,
        sender_type: 'admin',
        sender_id: 1
    };
    
    fetch('/messaging/send/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(messageData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('تم إرسال الرسالة بنجاح');
            closeAdminModals();
        } else {
            alert('حدث خطأ في الإرسال: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('حدث خطأ في الإرسال');
    });
}

function loadStudentMessages(studentId) {
    const messagesList = document.getElementById('studentMessagesList');
    
    fetch(`/messaging/student/${studentId}/messages/`)
        .then(response => response.json())
        .then(data => {
            if (data.messages && data.messages.length > 0) {
                let messagesHTML = '';
                data.messages.forEach(msg => {
                    messagesHTML += `
                        <div class="message-item ${msg.is_read ? '' : 'unread'}">
                            <div class="message-header">
                                <div class="message-title">${msg.title}</div>
                                <div class="message-time">${msg.created_at}</div>
                            </div>
                            <div class="message-content">${msg.content}</div>
                        </div>
                    `;
                });
                messagesList.innerHTML = messagesHTML;
            } else {
                messagesList.innerHTML = `
                    <div class="empty-messages">
                        لا توجد رسائل لهذا الطالب
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error loading messages:', error);
            messagesList.innerHTML = `
                <div class="empty-messages">
                    حدث خطأ في تحميل الرسائل
                </div>
            `;
        });
}