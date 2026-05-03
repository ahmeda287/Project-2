import os
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMainWindow
from gui import *


class Logic(QMainWindow, Ui_mainWindow):
    """
    A class representing the logic of a GUI television remote.
    Inherits from QMainWindow and the generated Ui_mainWindow class.
    """

    MIN_VOLUME: int = 0
    MAX_VOLUME: int = 10
    MIN_CHANNEL: int = 1
    MAX_FAVORITES: int = 6

    def __init__(self) -> None:
        """
        Method to initialize the Logic window, set default instance variables,
        and links all GUI signals to their handler methods.
        """
        super().__init__()
        self.setupUi(self)

        self.__status: bool = False
        self.__muted: bool = False
        self.__volume: int = Logic.MIN_VOLUME
        self.__max_channel: int = 0
        self.__channel: int = 0
        self.__channels: list[str] = []
        self.__folder: str = ''
        self.__favorites: list[str] = ['No favorite added', 'No favorite added', 'No favorite added',
                                       'No favorite added', 'No favorite added', 'No favorite added']

        self.power_button.clicked.connect(self.__power)
        self.mute_button.clicked.connect(self.__mute)
        self.volume_up.clicked.connect(self.__volume_up)
        self.volume_down.clicked.connect(self.__volume_down)
        self.channel_up.clicked.connect(self.__channel_up)
        self.channel_down.clicked.connect(self.__channel_down)
        self.set_current_channel.clicked.connect(self.__set_user_channel)
        self.add_current_to_favorites.clicked.connect(self.__add_favorite)
        self.remove_current_from_favorites.clicked.connect(
            self.__remove_favorite)

        self.favorite_1.clicked.connect(lambda: self.__set_to_favorite(0))
        self.favorite_2.clicked.connect(lambda: self.__set_to_favorite(1))
        self.favorite_3.clicked.connect(lambda: self.__set_to_favorite(2))
        self.favorite_4.clicked.connect(lambda: self.__set_to_favorite(3))
        self.favorite_5.clicked.connect(lambda: self.__set_to_favorite(4))
        self.favorite_6.clicked.connect(lambda: self.__set_to_favorite(5))

        self.load_channels.clicked.connect(self.__load_new_channels)
        self.volume_slider.valueChanged.connect(self.__slider_changed)

        self.__refresh_display()

    def __power(self) -> None:
        """
        Method to toggle the television on or off and refresh the display.
        """
        self.__status = not self.__status
        self.__clear_error()
        self.__refresh_display()

    def __mute(self) -> None:
        """
        Method to toggle mute when the television is on.
        Sets an error message if the television is off. 
        Refreshes the display.
        """
        if self.__status:
            self.__muted = not self.__muted
        else:
            self.__set_error('TV is off.')
        self.__refresh_display()

    def __volume_up(self) -> None:
        """
        Method to increase volume by one when the television is on.
        Unmutes the television if it is muted.
        Does not exceed the maximum volume.
        Sets an error message if the television is off.
        Refreshes the display.
        """
        if self.__status:
            if self.__muted:
                self.__mute()
            if self.__volume < Logic.MAX_VOLUME:
                self.__volume += 1
        else:
            self.__set_error('TV is off.')
        self.__refresh_display()

    def __volume_down(self) -> None:
        """
        Method to decrease volume by one when the television is on.
        Unmutes the television if it is muted.
        Does not go below the minimum volume.
        Sets an error message if the television is off.
        Refreshes the display.
        """
        if self.__status:
            if self.__muted:
                self.__mute()
            if self.__volume > Logic.MIN_VOLUME:
                self.__volume -= 1
        else:
            self.__set_error('TV is off.')
        self.__refresh_display()

    def __slider_changed(self, value: int) -> None:
        """
        Method to update volume when the slider value changes.
        Only applies when the television is on and the new value differs from the current volume.
        Sets an error message if the television is off.
        :param value: The slider value given by the volume slider widget.
        """
        if value == self.__volume:
            return
        if self.__status:
            self.__volume = value
            self.__refresh_display()
        else:
            self.__set_error('TV is off.')

    def __channel_up(self) -> None:
        """
        Method to increase the channel by one when the television is on.
        Wraps around to the minimum channel if already at the maximum.
        Sets an error message if no channels are loaded or the television is off.
        Refreshes the display.
        """
        if self.__status:
            if self.__max_channel == 0:
                self.__set_error('No channels loaded.')
                return
            if self.__channel == self.__max_channel:
                self.__channel = Logic.MIN_CHANNEL
            else:
                self.__channel += 1
        else:
            self.__set_error('TV is off.')
        self.__refresh_display()

    def __channel_down(self) -> None:
        """
        Method to decrease the channel by one when the television is on.
        Wraps around to the maximum channel if already at the minimum.
        Sets an error message if no channels are loaded or the television is off.
        Refreshes the display.
        """
        if self.__status:
            if self.__max_channel == 0:
                self.__set_error('No channels loaded.')
                return
            if self.__channel == Logic.MIN_CHANNEL or self.__channel == 0:
                self.__channel = self.__max_channel
            else:
                self.__channel -= 1
        else:
            self.__set_error('TV is off.')
        self.__refresh_display()

    def __set_channels(self, channels: list[str], max_channel: int) -> None:
        """
        Method to set the channel list and set the current channel to 0.
        :param channels: A list of channel name strings, with index 0 reserved as 'N/A'.
        :param max_channel: The total number of valid channels.
        """
        self.__channels = channels
        self.__max_channel = max_channel
        self.__channel = 0

    def __load_new_channels(self) -> None:
        """
        Method to load channels from a Channels.txt file in the specified folder provided by user.
        Finds favorites marked with '*fav*' and updates the channel list, favorite list, favorite buttons.
        Sets an error message for missing input, file not found, empty file, or read errors.
        Refreshes the display.
        """
        folder: str = self.channel_file_input_.text().strip()
        if folder == '':
            self.__set_error(
                'No folder entered.\nType the folder path containing your channel files.')
            return

        path: str = folder + os.sep + 'Channels.txt'

        try:
            with open(path, 'r') as input_file:
                lines: list[str] = input_file.readlines()
        except FileNotFoundError:
            self.__set_error(
                f'File not found:\n{path}\n\nCheck the folder path and try again.')
            return
        except Exception:
            self.__set_error('Could not read file.')
            return

        if len(lines) == 0:
            self.__set_error('File loaded but no channels found.')
            return

        self.__folder = folder
        channels: list[str] = ['N/A']
        favorites: list[str] = [''] * Logic.MAX_FAVORITES
        favorite_count: int = 0
        overflow_favorites: int = 0

        for line in lines:
            line = line.strip()
            if line == '':
                continue
            if line.lower().startswith('*fav*'):
                favorite: str = line[5:].strip()
                if favorite_count < Logic.MAX_FAVORITES:
                    favorites[favorite_count] = favorite
                    favorite_count += 1
                else:
                    overflow_favorites += 1
                channels.append(favorite)
            else:
                channels.append(line)

        self.__set_channels(channels, len(channels) - 1)
        self.__favorites = favorites
        self.channel_count.setText(f'Channel Count: {len(channels) - 1}')
        self.__refresh_fav_buttons()
        self.__set_error(
            f'Loaded {len(channels) - 1} channels successfully with {overflow_favorites} favorite overflows.')
        self.__refresh_display()

    def __set_user_channel(self) -> None:
        """
        Method to set the channel to a user-entered number.
        Validates that the input is a non-empty integer within the valid channel range.
        Sets an error message if the television is off, no channels are loaded, or input is invalid.
        Refreshes the display.
        """
        if not self.__status:
            self.__set_error('TV is off.')
            return
        if self.__max_channel == 0:
            self.__set_error('No channels loaded.')
            return

        user_input: str = self.channel_input.text().strip()
        if user_input == '':
            self.__set_error('Enter a channel number.')
            return

        try:
            index: int = int(user_input)
        except ValueError:
            self.__set_error(f'{user_input} is not a valid integer.')
            return

        if index < Logic.MIN_CHANNEL or index > self.__max_channel:
            self.__set_error(
                f'Channel {user_input} is out of range (Max: {self.__max_channel} Channels)')
            return

        self.__channel = index
        self.__clear_error()
        self.__refresh_display()

    def __add_favorite(self) -> None:
        """
        Method to add the current channel to the next open favorite slot.
        Sets an error message if the television is off, no channel is selected,
        the channel is already a favorite, or all favorite slots are full.
        Refreshes the favorite buttons only.
        """
        if not self.__status:
            self.__set_error('TV is off.')
            return
        if self.__channel == 0:
            self.__set_error('No channel is currently selected.')
            return

        current_name: str = self.__channels[self.__channel]

        if current_name in self.__favorites:
            self.__set_error(f"'{current_name}' is already a favorite.")
            return

        count: int = 0
        while count < Logic.MAX_FAVORITES:
            if self.__favorites[count] == 'No favorite added':
                self.__favorites[count] = current_name
                self.__refresh_fav_buttons()
                self.__set_error('Favorite added successfully.')
                return
            count += 1

        self.__set_error('All 6 favorite slots are taken.')

    def __remove_favorite(self) -> None:
        """
        Method to remove the current channel from favorites.
        Sets an error message if the television is off, no channel is selected,
        or the current channel is not in the favorites list.
        Refreshes the favorite buttons only..
        """
        if not self.__status:
            self.__set_error('TV is off.')
            return
        if self.__channel == 0:
            self.__set_error('No channel is currently tuned.')
            return

        current_name: str = self.__channels[self.__channel]

        if current_name not in self.__favorites:
            self.__set_error('Current channel is not in favorites.')
            return

        count: int = 0
        while count < Logic.MAX_FAVORITES:
            if self.__favorites[count] == current_name:
                self.__favorites[count] = 'No favorite added'
                self.__refresh_fav_buttons()
                self.__set_error('Favorite removed successfully.')
                return
            count += 1

    def __set_to_favorite(self, favorite_index: int) -> None:
        """
        Method to change current channel to the channel stored in the clicked favorite button.
        Sets an error message if the television is off or the slot is empty.
        :param favorite_index: The index of the favorite slot to navigate to.
        Refreshes display.
        """
        if not self.__status:
            self.__set_error('TV is off.')
            return

        favorite: str = self.__favorites[favorite_index]
        if favorite == 'No favorite added':
            self.__set_error('No favorite in this slot.')
            return

        count: int = 0
        while count < len(self.__channels):
            if self.__channels[count] == favorite:
                self.__channel = count
                self.__refresh_display()
                return
            count += 1

    def __update_channel_logo(self) -> None:
        """
        Method to display the logo image for the current channel.
        Looks for a .jpg then .png file matching the channel name in the loaded folder selected by user.
        Displays 'No Image' text if no matching image is found.
        """
        if self.__channel == 0 or self.__folder == '':
            self.channel_logo.clear()
            self.channel_logo.setText('No Image')
            return

        channel_name: str = self.__channels[self.__channel]
        image_path: str = self.__folder + os.sep + f'{channel_name}.jpg'
        if not os.path.exists(image_path):
            image_path = self.__folder + os.sep + f'{channel_name}.png'

        pixmap: QPixmap = QPixmap(image_path)
        if pixmap.isNull():
            self.channel_logo.clear()
            self.channel_logo.setText('No Image')
        else:
            self.channel_logo.setPixmap(pixmap.scaled(
                self.channel_logo.width(), self.channel_logo.height()))

    def __refresh_display(self) -> None:
        """
        Method to update all display labels and controls to the current television state.
        """
        if self.__channel > 0 and self.__max_channel > 0:
            self.current_channel.setText(
                f'Current Channel: {self.__channel} - {self.__channels[self.__channel]}')
        else:
            self.current_channel.setText('Current Channel: N/A')

        if self.__muted:
            self.Mute_status.setText('Mute Status: Muted')
            self.current_volume.setText(
                f'Current Volume: 0/{Logic.MAX_VOLUME}')
        else:
            self.Mute_status.setText('Mute Status: Not Muted')
            self.current_volume.setText(
                f'Current Volume: {self.__volume}/{Logic.MAX_VOLUME}')

        self.volume_slider.setValue(self.__volume)
        self.volume_slider.setEnabled(not self.__muted and self.__status)
        self.__update_channel_logo()

    def __refresh_fav_buttons(self) -> None:
        """
        Method to update the text of all six favorite buttons to match the current favorites list.
        """
        self.favorite_1.setText(self.__favorites[0])
        self.favorite_2.setText(self.__favorites[1])
        self.favorite_3.setText(self.__favorites[2])
        self.favorite_4.setText(self.__favorites[3])
        self.favorite_5.setText(self.__favorites[4])
        self.favorite_6.setText(self.__favorites[5])

    def __set_error(self, message: str) -> None:
        """
        Method to display an error/status message in the error label.
        :param message: The message string to display.
        """
        self.error_text.setText(message)

    def __clear_error(self) -> None:
        """
        Method to clear any existing message from the error label.
        """
        self.error_text.clear()
