import curses

from mpd import MPDClient

__version__ = "0.0.1"


class PDMPCClient(MPDClient):
    def __init__(self, host, port):
        super().__init__()
        self.timeout = 10
        self.idletimeout = None
        self.connect(host, port)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        self.disconnect()

    def window(self):
        k = 0
        cursor_x = 0
        cursor_y = 0

        screen = curses.initscr()

        # TODO: Merge positioning functions to reduce duplicate code

        def center(content, orientation=None):
            content_width = len(content)
            content_height = 1  # TODO: Get line-count
            if orientation == "H":
                return int((width // 2) - (content_width // 2))
            elif orientation == "V":
                return int((height // 2) - (content_height // 2 if content_height > 1 else 1))
            else:
                return int((height // 2) - (content_height // 2 if content_height > 1 else 1)), int((width // 2) - (content_width // 2))

        def align(content, orientation):
            content_width = len(content)
            content_height = 1  # TODO: Get line-count
            if orientation == "N":
                x_offset = 0
            elif orientation == "E":
                y_offset = width - content_width
            elif orientation == "S":
                x_offset = height - 1
            elif orientation == "W":
                y_offset = 0

            return y_offset

        # Start colors in curses
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_CYAN)

        while k != ord('q'):

            # Initialization
            screen.clear()
            # screen.bkgd(' ', curses.color_pair(3))
            height, width = screen.getmaxyx()

            # Key events
            if k == curses.KEY_DOWN:
                cursor_y = cursor_y + 1
            elif k == curses.KEY_UP:
                cursor_y = cursor_y - 1
            elif k == curses.KEY_RIGHT:
                cursor_x = cursor_x + 1
            elif k == curses.KEY_LEFT:
                cursor_x = cursor_x - 1

            # Rendering some text
            # whstr = f"Width: {width}, Height: {height}"
            # screen.addstr(0, 0, whstr, curses.color_pair(1))

            # Status bar
            # Tracklength, album, volume %
            # TODO: Create addstr function with color on/off and relative positioning support
            # Status Line 1
            track_progress = "0:69"
            track_length = "4:20"
            track_bitrate = "320"
            track_album = "Human Music"
            volume = "98"
            screen.addstr(0, 0, f"{track_progress}/{track_length} ({track_bitrate} kbps)")
            screen.addstr(0, center(track_album, "H"), f"{track_album}")
            screen.addstr(0, align(f"Vol: {volume}%", "E"), f"Vol: {volume}%")
            # Status line 2
            play_status = "playing"
            track_name = "The Bloops - Bleep (1993)"
            screen.addstr(1, 0, f"[{play_status}]")
            screen.addstr(1, center(track_name, "H"), f"{track_name}")
            screen.addstr(1, align("[------]", "E"), "[------]")
            # Divider
            screen.addstr(2, 0, f"{'─'*width}")
            # Playlist bar
            track_count = 42
            playlist_duration = "69 days, 4 hours, 20 minutes, 0 seconds"
            playlist_line = f"Playlist ({track_count} items, length: {playlist_duration})"
            screen.addstr(3, center(playlist_line, "H"), playlist_line)
            # Divider
            screen.addstr(4, 0, f"{'─' * width}")

            # Playlist
            mpd_version_string = f"MPD Version: {self.mpd_version}"
            pdmpc_version_string = f"PDMPC Version: {__version__}"
            screen.addstr(center(mpd_version_string, "V"), center(mpd_version_string, "H"), mpd_version_string)
            screen.addstr(center(pdmpc_version_string, "V") + 1, center(pdmpc_version_string, "H"), pdmpc_version_string)

            # Progress bar
            screen.attron(curses.color_pair(2))
            screen.addstr(height - 1, 0, f"{'-' * int(width - 1)}")
            screen.attroff(curses.color_pair(2))
            track_progress = f"{'=' * int(width // 2 - 1)}>"
            screen.attron(curses.color_pair(1))
            screen.addstr(height - 1, 0, track_progress)
            screen.attroff(curses.color_pair(1))

            # Refresh the screen
            screen.refresh()

            # Wait for next input
            k = screen.getch()
            curses.curs_set(0)


if __name__ == "__main__":
    with PDMPCClient("localhost", 6600) as mpc_client:
        # print(mpc_client.mpd_version)
        # print(mpc_client.status())
        # print(mpc_client.stats())
        mpc_client.window()
