# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8-80 compliant>

bl_info = {
    "name": "Push To Talk",
    "author": "Inês Almeida, Francesco Siddi",
    "version": (0, 1, 0),
    "blender": (2, 83, 0),
    "location": "Video Sequence Editor",
    "description": "To Do",
    "doc_url": "{BLENDER_MANUAL_URL}/addons/sequencer/XXX.html",
    "category": "Sequencer",
}


import bpy
from bpy.types import Operator
from bpy.props import BoolProperty


class SEQUENCER_OT_push_to_talk(Operator):
    bl_idname = "sequencer.push_to_talk"
    bl_label = "Start Recording"
    bl_description = "XXX"
    bl_options = {'UNDO', 'REGISTER'}

    should_stop = False

    # Runtime state
    is_running = False


    def add_visual_feedback_strip(self, context):
        bpy.ops.sequencer.effect_strip_add(
            type='COLOR',
            frame_start=context.scene.frame_current,
            frame_end=80,
            channel=1,
            replace_sel=True,
            overlap=False,
            color=(0.5607842206954956, 0.21560697257518768, 0.1903851181268692)
        )
        new_strip = context.scene.sequence_editor.sequences_all['Color']
        new_strip.name = "Recording..."

    @classmethod
    def poll(cls, context):
        return (context.space_data.view_type in {'SEQUENCER', 'SEQUENCER_PREVIEW'})
        #return (context.sequences)


    def invoke(self, context, event):
        print("TALK - invoke")

        # If this operator is already running modal, this second invocation is
        # the toggle to stop it. Set a variable that the first modal operator
        # instance will listen to.
        if (SEQUENCER_OT_push_to_talk.is_running):
            SEQUENCER_OT_push_to_talk.should_stop = True
            return {'FINISHED'}

        SEQUENCER_OT_push_to_talk.is_running = True

        self.add_visual_feedback_strip(context)

        self.was_playing = context.screen.is_animation_playing
        if (self.was_playing == False):
            bpy.ops.screen.animation_play()

        print("TALK - running modal")
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.02, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}


    def modal(self, context, event):

        #print(event.type)

        # Cancel. Delete the current recording.
        if event.type in {'ESC'}:
            print("modal - cancel")
            self.cancel(context)
            return {'CANCELLED'}

        # Confirm. Delete the current recording.
        if event.type in {'RET'}:
            print("modal - confirm")
            return self.execute(context)

        # Periodic update
        if event.type == 'TIMER':

            # Listen for signal to stop
            if (SEQUENCER_OT_push_to_talk.should_stop):
                return self.execute(context)

            # Draw
            sequence_ed = context.scene.sequence_editor
            color_strip = sequence_ed.sequences_all["Recording..."]
            color_strip.frame_final_end = context.scene.frame_current

        return {'PASS_THROUGH'}


    def on_cancel_or_finish(self, context):
        print("restore_playing_state")

        wm = context.window_manager
        wm.event_timer_remove(self._timer)

        SEQUENCER_OT_push_to_talk.is_running = False
        SEQUENCER_OT_push_to_talk.should_stop = False

        if (not self.was_playing):
            bpy.ops.screen.animation_play()


    def execute(self, context):
        print("TALK - execute")

        self.on_cancel_or_finish(context)

        sequence_ed = context.scene.sequence_editor

        # Gather the position information from the dummy strip and delete it.
        color_strip = sequence_ed.sequences_all["Recording..."]
        channel = color_strip.channel
        frame_start = color_strip.frame_final_start
        bpy.ops.sequencer.delete()

        # Create a new sound strip in the place of the dummy strip
        sound_strip = sequence_ed.sequences.new_sound(
            "Waa", "/home/stitch/out.wav",
            channel, frame_start
        )

        return {'FINISHED'}


    def cancel(self, context):
        print("TALK - cancel")

        self.on_cancel_or_finish(context)
        bpy.ops.sequencer.delete()




class SEQUENCER_OT_push_to_stop(Operator):
    bl_idname = "sequencer.push_to_stop"
    bl_label = "Stop Recording"
    bl_description = "XXX"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):
        print("STOP - execute")
        SEQUENCER_OT_push_to_talk.should_stop
        return {'FINISHED'}


def draw_push_to_talk_button(self, context):
    layout = self.layout
    if (SEQUENCER_OT_push_to_talk.is_running):
        layout.operator("sequencer.push_to_talk", text="Stop Recording", icon='SNAP_FACE') #PAUSE
    else:
        layout.operator("sequencer.push_to_talk", text="Start Recording", icon='REC') #PLAY_SOUND



# Add-on Registration #########################################################

classes = (
    SEQUENCER_OT_push_to_talk,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.SEQUENCER_HT_header.append(draw_push_to_talk_button)


def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
