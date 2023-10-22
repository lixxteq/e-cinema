from flask import flash
from markupsafe import Markup

# Использует заготовленный HTML для отображения flash-сообщений в виде само-исчезающих алертов
def flash_alert(message, category):
    alert = Markup(f"""
    <div class="alert alert-{category} alert-dismissible fade show w-25 position-fixed mt-3 ms-3" role="alert" style="opacity: 0.98;">
      {message}
    </div>
    <script>
        setTimeout(() => document.getElementById('alert-block').remove(), 5000);
    </script>
    """)
    flash(alert, category)