"""Base classes for widgets."""

import abc

from ipywidgets import HBox, Layout, Output, VBox


def metaclass_resolver(*classes):
    """Merge multiple meta classes."""
    # Does something like this:
    # https://coderedirect.com/questions/163000/multiple-inheritance-metaclass-conflict
    metaclass = tuple({type(cls) for cls in classes})

    def cls_name(classes):
        return "_".join(mcls.__name__ for mcls in classes)

    metaclass = metaclass[0] if len(metaclass) == 1 else type(cls_name(metaclass), metaclass, {})  # class M_C
    return metaclass(cls_name(classes), classes, {})  # class C


class _merged_meta(type(abc.ABC)):  # avoid metaclass conflict.
    pass


class WidgetBase(abc.ABC, metaclass=_merged_meta):
    """Base class for weldx widgets."""

    def copy(self):
        """Copy the widget."""
        from copy import deepcopy

        return deepcopy(self)

    def set_visible(self, state: bool):
        """Toggle visibility."""
        if not hasattr(self, "layout"):
            raise NotImplementedError
        if state:
            visibility = "visible"
        else:
            visibility = "hidden"
        self.layout.visibility = visibility


border_debug_style = ""  # 2px dashed green"
margin = ""  # "10px"


class WidgetMyHBox(metaclass_resolver(HBox, WidgetBase)):
    """Wrap around a HBox sharing a common layout."""

    def __init__(self, *args, **kwargs):
        if "layout" in kwargs:
            layout = kwargs["layout"]
        else:
            layout = Layout()
            kwargs["layout"] = layout
        layout.border = border_debug_style
        layout.margin = margin

        super().__init__(*args, **kwargs)


class WidgetMyVBox(metaclass_resolver(VBox, WidgetBase)):
    """Wrap around a VBox sharing a common layout."""

    def __init__(self, *args, **kwargs):
        if "layout" in kwargs:
            layout = kwargs["layout"]
        else:
            layout = Layout()
            kwargs["layout"] = layout
        layout.border = border_debug_style
        layout.margin = margin

        super().__init__(*args, **kwargs)


class WidgetSimpleOutput(WidgetMyHBox):
    """Wrap around a ipywidgets.Output."""

    def __init__(self, out=None, height=None, width=None):
        if out is None:
            from .widget_factory import copy_layout, layout_generic_output

            if height or width:
                layout = copy_layout(layout_generic_output)
                if height:
                    layout.height = height
                if width:
                    layout.width = width
            else:
                layout = layout_generic_output
            out = Output(layout=layout)
        else:
            layout = out.layout
        self.out = out
        super().__init__(children=[self.out], layout=layout)

    def __enter__(self):
        """Enter."""
        return self.out.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit."""
        return self.out.__exit__(exc_type, exc_val, exc_tb)


class WeldxImportExport(abc.ABC):
    """Abstract import and export interfaces for weldx data exchange."""

    @abc.abstractmethod
    def from_tree(self, tree: dict):
        """Fill the widget with given state dictionary."""

    @abc.abstractmethod
    def to_tree(self) -> dict:
        """Return a dict containing data from widget."""
