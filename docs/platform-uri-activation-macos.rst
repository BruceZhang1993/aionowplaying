macOS URI Activation
====================

This page shows the host-side part of URI activation on macOS.

Why the library cannot do this alone
------------------------------------

``aionowplaying`` is a library, not a macOS application bundle. URI activation
on macOS is delivered to an installed ``.app`` that registers a URL type in its
``Info.plist``. Without that host bundle, there is nowhere for the operating
system to send the activation event.

That means the library can help with opening a URI from the current process, but
the host application must still register the scheme and receive the activated
URI.

What the host needs to do
-------------------------

The host application must:

* choose a custom scheme
* add the scheme to ``CFBundleURLTypes`` in ``Info.plist``
* receive the URL in the app delegate or scene lifecycle
* forward the URI to playback logic

Minimal reference
-----------------

The example below uses a host-defined scheme such as ``myplayer://``. Replace
the scheme name with one that belongs to your application.

.. code-block:: swift

    import Cocoa

    @main
    class AppDelegate: NSObject, NSApplicationDelegate {
        private let player = PlayerController()

        func application(_ application: NSApplication,
                         open urls: [URL]) {
            for url in urls {
                handleActivatedURI(url.absoluteString)
            }
        }

        private func handleActivatedURI(_ uri: String) {
            player.handleActivatedURI(uri)
        }
    }

.. code-block:: xml

    <key>CFBundleURLTypes</key>
    <array>
      <dict>
        <key>CFBundleURLName</key>
        <string>com.example.myplayer</string>
        <key>CFBundleURLSchemes</key>
        <array>
          <string>myplayer</string>
        </array>
      </dict>
    </array>

Returning the URI to player logic
---------------------------------

Keep URI parsing out of the app delegate when possible. A small player-facing
method keeps the activation path simple:

.. code-block:: swift

    final class PlayerController {
        func handleActivatedURI(_ uri: String) {
            // Parse the URI and decide whether to open, queue, or play it.
            print("Activated URI:", uri)
        }
    }

If your player already has a command handler, route the URI there instead of
duplicating playback rules in the macOS lifecycle code.
