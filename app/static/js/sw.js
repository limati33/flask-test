self.addEventListener('push', function(event) {
    const data = event.data.json(); // Данные из уведомления
    self.registration.showNotification(data.title, {
        body: data.body,
        icon: '/static/images/icon.png' // Путь к иконке
    });
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    event.waitUntil(
        clients.openWindow('/') // Перенаправляем на главную страницу
    );
});
