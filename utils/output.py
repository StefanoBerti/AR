import cv2
from vispy import app, scene, visuals
from vispy.color import Colormap
from vispy.scene.visuals import Text, Image, ColorBar
import numpy as np
import math


class VISPYVisualizer:

    def printer(self, x):
        if x.text == '\b':
            if len(self.input_text) > 1:
                self.input_text = self.input_text[:-1]
            self.log.text = ''
        elif x.text == '\r':
            self.output_queue.put(self.input_text[1:])  # Do not send '<'
            self.input_text = '>'
            self.log.text = ''
        elif x.text == '\\':
            self.show = not self.show
        elif x.text == '`':
            self.os = not self.os
        else:
            self.input_text += x.text
        self.input_string.text = self.input_text

    @staticmethod
    def create_visualizer(qi, qo):
        _ = VISPYVisualizer(qi, qo)
        app.run()

    def __init__(self, input_queue, output_queue):

        self.input_queue = input_queue
        self.output_queue = output_queue
        self.show = True

        self._timer = app.Timer('auto', connect=self.on_timer, start=True)
        self.input_text = '>'

        self.canvas = scene.SceneCanvas(keys='interactive')
        self.canvas.size = 1200, 600
        self.canvas.show()
        self.canvas.events.key_press.connect(self.printer)

        self.os = False

        # This is the top-level widget that will hold three ViewBoxes, which will
        # be automatically resized whenever the grid is resized.
        grid = self.canvas.central_widget.add_grid()

        # Plot
        b1 = grid.add_view(row=0, col=0)
        b1.border_color = (0.5, 0.5, 0.5, 1)
        b1.camera = scene.TurntableCamera(45, elevation=30, azimuth=0, distance=2)
        self.lines = []
        Plot3D = scene.visuals.create_visual_node(visuals.LinePlotVisual)
        for _ in range(30):
            self.lines.append(Plot3D(
                [],
                width=3.0,
                color="purple",
                edge_color="w",
                symbol="o",
                face_color=(0.2, 0.2, 1, 0.8),
                marker_size=1,
            ))
            b1.add(self.lines[_])
        coords = scene.visuals.GridLines(parent=b1.scene)

        # Info
        self.b2 = grid.add_view(row=0, col=1)
        self.b2.camera = scene.PanZoomCamera(rect=(0, 0, 1, 1))
        self.b2.camera.interactive = False
        self.b2.border_color = (0.5, 0.5, 0.5, 1)
        self.distance = Text('', color='white', rotation=0, anchor_x="center", anchor_y="bottom",
                             font_size=12, pos=(0.25, 0.9))
        self.b2.add(self.distance)
        self.focus = Text('', color='green', rotation=0, anchor_x="center", anchor_y="bottom",
                          font_size=12, pos=(0.5, 0.9))
        self.b2.add(self.focus)
        self.fps = Text('', color='white', rotation=0, anchor_x="center", anchor_y="bottom",
                        font_size=12, pos=(0.75, 0.9))
        self.is_same_action = Text('', color='white', rotation=0, anchor_x="center", anchor_y="bottom",
                                   font_size=12, pos=(0.75, 0.7))
        self.b2.add(self.is_same_action)
        self.b2.add(self.fps)
        self.actions = {}
        self.values = {}

        # Image
        b3 = grid.add_view(row=1, col=0)
        b3.camera = scene.PanZoomCamera(rect=(0, 0, 640, 480))
        b3.camera.interactive = False
        b3.border_color = (0.5, 0.5, 0.5, 1)
        self.image = Image()
        b3.add(self.image)

        # Commands
        b4 = grid.add_view(row=1, col=1)
        b4.camera = scene.PanZoomCamera(rect=(0, 0, 1, 1))
        b4.camera.interactive = False
        b4.border_color = (0.5, 0.5, 0.5, 1)
        self.desc_add = Text('ADD ACTION: add action_name [-focus]', color='white', rotation=0,
                             anchor_x="left",
                             anchor_y="bottom",
                             font_size=12, pos=(0.1, 0.9))
        self.desc_remove = Text('REMOVE ACTION: remove action_name', color='white', rotation=0, anchor_x="left",
                                anchor_y="bottom",
                                font_size=12, pos=(0.1, 0.7))
        self.input_string = Text(self.input_text, color='purple', rotation=0, anchor_x="left", anchor_y="bottom",
                                 font_size=12, pos=(0.1, 0.5))
        self.log = Text('', color='orange', rotation=0, anchor_x="left", anchor_y="bottom",
                        font_size=12, pos=(0.1, 0.3))
        b4.add(self.desc_add)
        b4.add(self.desc_remove)
        b4.add(self.input_string)
        b4.add(self.log)

    def on_timer(self, _):
        # if not self.is_running:
        #     self.canvas.close()
        #     exit()
        if not self.show:
            return
        # Check if there is something to show
        elements = self.input_queue.get()
        if not elements:
            return
        # Parse elements
        elements = elements[0]
        if "log" in elements.keys():
            self.log.text = elements["log"]
        else:
            edges = elements["edges"] if "edges" in elements.keys() else None
            pose = elements["pose"] if "pose" in elements.keys() else None
            img = elements["img"]
            focus = elements["focus"] if "focus" in elements.keys() else None
            fps = elements["fps"]
            results = elements["actions"] if "actions" in elements.keys() else None
            is_true = elements["is_true"] if "is_true" in elements.keys() else None
            distance = elements["distance"] if "distance" in elements.keys() else None
            bbox = elements["bbox"] if "bbox" in elements.keys() else None

            # POSE
            if pose is not None:  # IF pose is not None, edges is not None
                theta = 90
                R = np.matrix([[1, 0, 0],
                               [0, math.cos(theta), -math.sin(theta)],
                               [0, math.sin(theta), math.cos(theta)]])
                pose = pose @ R
                for i, edge in enumerate(edges):
                    self.lines[i].set_data((pose[[edge[0], edge[1]]]))

            # IMAGE
            img = cv2.flip(img, 0)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            if bbox is not None:
                x1, x2, y1, y2 = bbox
                img = cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 1)
            self.image.set_data(img)

            # INFO
            if focus:
                self.focus.text = "FOCUS"
                self.focus.color = "green"
            else:
                self.focus.text = "NOT FOC."
                self.focus.color = "red"
            self.fps.text = "FPS: {:.2f}".format(fps)
            self.distance.text = "DIST: {:.2f}m".format(distance) if distance is not None else "DIST:"

            m = max(results.values()) if len(results) > 0 else 0  # Just max
            for i, r in enumerate(results.keys()):
                score = results[r]
                requires_focus = False
                # Check if conditions are satisfied
                if score == m:
                    # OS SCORE
                    if self.os:
                        self.is_same_action.text = "{:.2f}".format(float(is_true))
                        self.is_same_action.color = 'red' if float(is_true) < 0.75 else 'green'
                        self.is_same_action.pos = 0.75, 0.7 - (0.1 * i)
                    else:
                        self.is_same_action.text = ""
                    c1 = True if not requires_focus else focus
                    c2 = float(is_true) >= 0.75
                    if self.os:
                        if c1 and c2:
                            color = "green"
                        else:
                            color = "orange"
                    else:
                        if c1:
                            color = "green"
                        else:
                            color = "orange"
                else:
                    color = "red"
                if r in self.actions.keys():
                    text = r  # {:.2f}".format(r, score)
                    if requires_focus:
                        text += ' (0_0)'
                    self.actions[r].text = text
                else:
                    self.actions[r] = Text('', rotation=0, anchor_x="center", anchor_y="bottom", font_size=12)
                    self.values[r] = ColorBar(Colormap(['r', 'g']), "top", (0.5, 0.05), clim=("", ""))
                    self.b2.add(self.actions[r])
                    self.b2.add(self.values[r])

                bar_height = 0.075
                self.values[r].label = "{:.2f}".format(score)
                self.values[r].pos = 0.5 + (score/4 if score/2 > bar_height else bar_height/2), \
                                     0.7 - (0.1 * i) - bar_height/2
                self.values[r].size = (score/2 if score/2 > bar_height else bar_height, bar_height)
                self.actions[r].pos = 0.25, 0.7 - (0.1 * i)
                self.actions[r].color = color

            # Remove erased action (if any)
            to_remove = []
            for key in self.actions.keys():
                if key not in results.keys():
                    to_remove.append(key)
            for key in to_remove:
                self.actions[key].parent = None
                self.values[key].parent = None
                self.actions.pop(key)
                self.values.pop(key)

    def on_draw(self, event):
        pass
