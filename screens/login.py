"""Login screen."""

import datetime

import textual.app
import textual.containers
import textual.reactive
import textual.screen
import textual.widgets

import utils.save

# TODO: errors?
# TODO: should probably do lowercase usernames


class ListUsersScreen(textual.screen.ModalScreen):
    """List users modal screen."""

    def compose(self) -> textual.app.ComposeResult:
        """Compose th ui."""
        with textual.containers.Container(id="llist_box"):
            yield textual.widgets.Label("Existing users", id="llist_title")
            yield textual.widgets.Rule(id="llist_rule")
            with textual.containers.Vertical(id="llist_ver"):
                yield from [textual.widgets.Label(user, classes="llist_label")
                            for user in utils.save.get_newest_saves()]
            with textual.containers.Horizontal(id="llist_hor"):
                yield textual.widgets.Button("close", id="llist_close", classes="login_button")

    @textual.on(textual.widgets.Button.Pressed, "#llist_close")
    def pressed_llist_close(self, event: textual.widgets.Button.Pressed) -> None:
        """Handle button pressed event for llist_close."""
        event.stop()
        self.app.pop_screen()


class CreateUserScreen(textual.screen.ModalScreen):
    """Create user modal screen."""

    def on_mount(self) -> None:
        """Do stuff on mount."""
        self.query_one("#lcreate_user").border_title = "username"
        self.query_one("#lcreate_pwd").border_title = "password"

    def compose(self) -> textual.app.ComposeResult:
        """Compose the ui."""
        with textual.containers.Container(id="lcreate_box"):
            yield textual.widgets.Label("Create new user", id="lcreate_title")
            yield textual.widgets.Input(id="lcreate_user")
            yield textual.widgets.Input(id="lcreate_pwd")
            with textual.containers.Horizontal(id="lcreate_hor"):
                yield textual.widgets.Button("create", id="lcreate_create", classes="login_button")
                yield textual.widgets.Button("cancel", id="lcreate_cancel", classes="login_button")

    @textual.on(textual.widgets.Button.Pressed, "#lcreate_create")
    def pressed_lcreate_create(self, event: textual.widgets.Button.Pressed) -> None:
        """Hande button pressed event for lcreate_create."""
        event.stop()
        user = self.query_one("#lcreate_user", textual.widgets.Input)
        pwd = self.query_one("#lcreate_pwd", textual.widgets.Input)
        username: str = user.value
        password: str = pwd.value
        # handle all possible errors
        if username == "":
            self.notify("Username can't be empty.", severity="error")
        elif username == "zer0":
            self.notify("Sorry, that's taken ;)", severity="error")
        elif username in utils.save.get_newest_saves():
            self.notify("Username already used.", severity="error")
        elif not username.isalnum():
            self.notify("Username may only contain alpanumeric characters.",
                        severity="error")
        elif password == "":
            self.notify("Password can't be empty.", severity="error")
        else:
            utils.save.Save.create(username, password).save()
            self.app.pop_screen()

    @textual.on(textual.widgets.Button.Pressed, "#lcreate_cancel")
    def pressed_lcreate_cancel(self, event: textual.widgets.Button.Pressed) -> None:
        """Hande button pressed event for lcreate_cancel."""
        event.stop()
        self.app.pop_screen()


class LoginScreen(textual.screen.Screen):
    """Login screen."""

    time = textual.reactive.reactive(datetime.datetime.now)

    def login(self) -> bool:
        """Log in to computer."""
        saves: dict[str, utils.save.Save] = utils.save.get_newest_saves()
        user = self.query_one("#login_user", textual.widgets.Input)
        pwd = self.query_one("#login_pwd", textual.widgets.Input)
        if (save := saves.get(user.value)) is not None:
            if save.password == pwd.value:
                user.clear()
                pwd.clear()
                user.focus()
                return True
            else:
                self.notify("Wrong password.", severity="error")
        else:
            self.notify("User does not exist.", severity="error")
        return False

    def update_time(self) -> None:
        """Update the time attribute."""
        self.time = datetime.datetime.now()

    def watch_time(self, time: datetime.datetime) -> None:
        """Watch the time attribute."""
        self.query_one("#login_clock", textual.widgets.Digits).update(
            time.strftime("%H:%M"))

    def on_mount(self) -> None:
        """Do stuff on mount."""
        self.query_one("#login_user").border_title = "username"
        self.query_one("#login_pwd").border_title = "password"
        self.set_interval(1, self.update_time)

    def compose(self) -> textual.app.ComposeResult:
        """Compose the ui."""
        with textual.containers.Vertical(id="login_vert"):
            yield textual.widgets.Digits(id="login_clock")
            yield textual.widgets.Input(id="login_user")
            yield textual.widgets.Input(password=True, id="login_pwd")
            with textual.containers.Horizontal(id="login_box"):
                yield textual.widgets.Button("log in", id="login_button", classes="login_button")
        with textual.containers.Horizontal(id="login_hor"):
            yield textual.widgets.Button("list users", id="login_list", classes="login_button")
            yield textual.widgets.Button("create user", id="login_create", classes="login_button")
            yield textual.widgets.Button("shutdown", id="login_shutdown", classes="login_button")

    def on_input_submitted(self, event: textual.widgets.Input.Submitted) -> None:
        """Handle input submitted event."""
        event.stop()
        if self.login():
            self.app.push_screen("desktop")

    @textual.on(textual.widgets.Button.Pressed, "#login_button")
    def login_button_pressed(self, event: textual.widgets.Button.Pressed) -> None:
        """Handle on button pressed for the login_button."""
        event.stop()
        if self.login():
            self.app.push_screen("desktop")

    @textual.on(textual.widgets.Button.Pressed, "#login_list")
    def login_list_pressed(self, event: textual.widgets.Button.Pressed) -> None:
        """Handle on button pressed for the login_list."""
        event.stop()
        self.app.push_screen(ListUsersScreen())

    @textual.on(textual.widgets.Button.Pressed, "#login_create")
    def login_create_pressed(self, event: textual.widgets.Button.Pressed) -> None:
        """Handle on button pressed for the login_create."""
        event.stop()
        self.app.push_screen(CreateUserScreen())

    @textual.on(textual.widgets.Button.Pressed, "#login_shutdown")
    def login_shutdown_pressed(self, event: textual.widgets.Button.Pressed) -> None:
        """Handle on button pressed for the login_shutdown."""
        event.stop()
        self.app.exit()
