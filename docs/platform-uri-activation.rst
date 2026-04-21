URI Activation Overview
=======================

``aionowplaying`` can help a running process open a URI, but it does not turn
the library into a desktop app host. URI activation is a two-part problem:

1. The current process may open a URI on purpose.
2. The host application must register a custom scheme and receive the activated
   URI from the operating system.

The library can support the first part directly. The second part belongs to the
host application, because the OS delivers URI activation to an installed app or
bundle, not to a standalone Python library.

What the library can do
-----------------------

The library can expose a small API for opening URIs from the current process.
That is useful when your player wants to hand a link to the platform default
handler or open a resource in the system browser.

What the host must do
---------------------

The host application is still responsible for:

* choosing a custom scheme
* registering that scheme with the OS
* receiving the activation event or launch arguments
* parsing the URI
* forwarding the URI to playback logic

The scheme is host-defined. ``aionowplaying`` does not require ``aionowplaying``
as the public scheme name. A host can use values such as ``myplayer://`` or any
other scheme that fits its product.

How the pieces fit together
---------------------------

The most practical shape is:

* ``aionowplaying`` provides the media abstraction and a helper for opening a
  URI from the current process.
* The host registers a custom scheme and handles activation.
* The host passes the activated URI into the player layer, which can then decide
  whether to open it, queue it, or play it directly.

For platform examples, see:

.. toctree::
   :maxdepth: 1

   platform-uri-activation-macos
   platform-uri-activation-windows
