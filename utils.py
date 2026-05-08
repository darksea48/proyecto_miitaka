from django import forms


class BootstrapFormMixin:
    """Aplica clases Bootstrap a widgets de formularios automáticamente."""

    _FORM_CONTROL = (
        forms.TextInput, forms.NumberInput, forms.EmailInput,
        forms.Textarea, forms.DateTimeInput, forms.DateInput,
        forms.TimeInput, forms.URLInput, forms.PasswordInput,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, self._FORM_CONTROL):
                widget.attrs.setdefault('class', 'form-control')
            elif isinstance(widget, forms.Select):
                widget.attrs.setdefault('class', 'form-select')
            elif isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault('class', 'form-check-input')
