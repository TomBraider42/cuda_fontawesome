Font Awesome
Plugin for CudaText

Search Font Awesome icons in sidebar and insert the codes in current editor.

=== IMPORTANT ============================================
Besure you have installed the fonts from vendor/fonts.zip.
==========================================================

Check Plugins -> Font Awesome -> Config for code format.

Default (for HTML):
{
	"code_format": "<i class=\"{font} fa-{name}\"></i> "
}

Possible variables:

{font}    far|fas|fab for Regular, Solid, Brands
{name}    e.g. "address-card"
{unicode} e.g. "\uf2bb"
{hexcode} e.g. "F2BB"

Uses the free version from https://fontawesome.com

Author: Tom Braider
License: MIT
