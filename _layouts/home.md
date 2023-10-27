---
layout: home
---
<!DOCTYPE html>
<html>

<head>
    {% include head.html %}
</head>

<body>
    <div class="container" id="main-container">
        {% include header.html %}
        {{ content }}
        {% include footer.html %}
    </div>
</body>

</html>
