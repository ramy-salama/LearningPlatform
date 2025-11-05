from django.shortcuts import redirect

def teacher_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('teacher_id'):
            return redirect('teacher_login')
        return view_func(request, *args, **kwargs)
    return wrapper