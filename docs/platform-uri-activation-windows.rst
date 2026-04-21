Windows URI Activation
======================

This page shows the host-side part of URI activation on Windows.

Why the library cannot do this alone
------------------------------------

``aionowplaying`` can help a running process open a URI, but Windows URI
activation is owned by the installed host application. The operating system
delivers custom-scheme launches to the app registration, packaged app manifest,
or desktop installation entry. A standalone library does not receive those
events on its own.

What the host needs to do
-------------------------

The host application must:

* choose a custom scheme
* register that scheme for the app
* read the activation URI from launch data or command-line arguments
* forward the URI to playback logic

Minimal reference
-----------------

The example below uses a host-defined scheme such as ``myplayer://``. Replace
the scheme name with one that belongs to your application.

Packaged apps can read activation arguments from the app activation event. For a
desktop-style host, the same URI can also be forwarded through the command line
when the app is launched by the shell.

.. code-block:: python

    import sys

    class PlayerController:
        def handle_activated_uri(self, uri: str) -> None:
            # Parse the URI and decide whether to open, queue, or play it.
            print(f"Activated URI: {uri}")

    def main() -> None:
        player = PlayerController()

        # Example command-line activation:
        # myplayer://open?target=https%3A%2F%2Fexample.com%2Ftrack
        if len(sys.argv) > 1 and sys.argv[1].startswith("myplayer://"):
            player.handle_activated_uri(sys.argv[1])

    if __name__ == "__main__":
        main()

.. code-block:: xml

    <Applications>
      <Application Id="App" Executable="$targetnametoken$.exe" EntryPoint="Windows.FullTrustApplication">
        <Extensions>
          <uap:Extension Category="windows.protocol">
            <uap:Protocol Name="myplayer" />
          </uap:Extension>
        </Extensions>
      </Application>
    </Applications>

Returning the URI to player logic
---------------------------------

The host should normalize the URI first, then hand it to the player layer in a
single place:

.. code-block:: python

    def handle_activated_uri(player, uri: str) -> None:
        # Keep the activation bridge thin.
        player.handle_activated_uri(uri)

If your app uses a dedicated playback service, let the host code call that
service directly. The important part is that activation handling stays outside
``aionowplaying`` while the playback decision stays inside your player layer.
