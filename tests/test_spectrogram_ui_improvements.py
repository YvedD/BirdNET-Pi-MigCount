#!/usr/bin/env python3
"""
Comprehensive test for spectrogram UI improvements.

Tests:
1. Colorbar label settings are correctly configured
2. Title font size has been increased
3. No regressions in existing functionality
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_colorbar_label_configuration():
    """Verify colorbar label is configured with proper settings."""
    reporting_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'scripts',
        'utils',
        'reporting.py'
    )
    
    with open(reporting_path, 'r') as f:
        content = f.read()
    
    # Check that colorbar uses increased padding
    assert 'pad=0.15' in content, \
        "Colorbar pad should be increased to 0.15"
    
    # Check that label uses ax.set_ylabel method
    assert 'cbar.ax.set_ylabel(' in content, \
        "Colorbar should use cbar.ax.set_ylabel() for label"
    
    # Check label positioning is explicitly set
    assert "cbar.ax.yaxis.set_label_position('right')" in content, \
        "Colorbar label position should be explicitly set to 'right'"
    
    # Check rotation is set
    assert 'rotation=270' in content or 'rotation=-90' in content, \
        "Colorbar label should have rotation specified"
    
    # Check labelpad is increased
    assert 'labelpad=20' in content or 'labelpad=15' in content, \
        "Colorbar labelpad should be increased (15 or 20)"
    
    # Check verticalalignment is set
    assert "verticalalignment='bottom'" in content, \
        "Colorbar label should have verticalalignment set"
    
    # Check that PCEN dB label text is still present
    assert '"PCEN dB"' in content, \
        'Colorbar label should still be "PCEN dB"'
    
    print("✓ Colorbar label configuration checks passed")


def test_title_font_size_increased():
    """Verify title font size has been increased."""
    reporting_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'scripts',
        'utils',
        'reporting.py'
    )
    
    with open(reporting_path, 'r') as f:
        lines = f.readlines()
    
    # Find the title_font line
    title_font_lines = [line for line in lines if 'title_font = ImageFont.truetype' in line]
    assert len(title_font_lines) == 1, "Should find exactly one title_font definition"
    
    title_font_line = title_font_lines[0]
    
    # Extract font size - should be at least 18 (we used 20)
    import re
    match = re.search(r'ImageFont\.truetype\([^,]+,\s*(\d+)\)', title_font_line)
    assert match, "Should find font size in title_font line"
    
    font_size = int(match.group(1))
    assert font_size >= 18, f"Title font size should be at least 18, got {font_size}"
    print(f"✓ Title font size is {font_size} (>= 18)")


def test_no_regressions():
    """Verify no regressions in existing functionality."""
    reporting_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'scripts',
        'utils',
        'reporting.py'
    )
    
    with open(reporting_path, 'r') as f:
        content = f.read()
    
    # Check essential elements still exist
    assert 'TARGET_DPI = 200' in content, \
        "DPI constant should remain unchanged"
    
    assert 'TARGET_FIGSIZE = (10.0, 5.0)' in content, \
        "Figure size should remain unchanged"
    
    assert 'constrained_layout=True' in content, \
        "Constrained layout should still be used"
    
    assert 'librosa.pcen(' in content, \
        "PCEN processing should still be present"
    
    assert 'cmap="plasma"' in content, \
        "Plasma colormap should still be used"
    
    assert 'cbar.set_ticks([vmin, vmax])' in content, \
        "Colorbar min/max ticks should still be set"
    
    assert 'ax.xaxis.set_major_locator(mticker.MultipleLocator(1.0))' in content, \
        "X-axis major locator should still be 1.0s"
    
    assert 'ax.xaxis.set_minor_locator(mticker.MultipleLocator(0.1))' in content, \
        "X-axis minor locator should still be 0.1s"
    
    assert 'facecolor="black"' in content, \
        "Black background should still be used"
    
    print("✓ No regressions - all essential elements present")


def test_comment_font_unchanged():
    """Verify comment font size remains unchanged."""
    reporting_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'scripts',
        'utils',
        'reporting.py'
    )
    
    with open(reporting_path, 'r') as f:
        lines = f.readlines()
    
    # Find the comment_font line
    comment_font_lines = [line for line in lines if 'comment_font = ImageFont.truetype' in line]
    assert len(comment_font_lines) == 1, "Should find exactly one comment_font definition"
    
    comment_font_line = comment_font_lines[0]
    
    # Extract font size - should still be 11
    import re
    match = re.search(r'ImageFont\.truetype\([^,]+,\s*(\d+)\)', comment_font_line)
    assert match, "Should find font size in comment_font line"
    
    font_size = int(match.group(1))
    assert font_size == 11, f"Comment font size should remain 11, got {font_size}"
    print(f"✓ Comment font size unchanged at {font_size}")


if __name__ == '__main__':
    import traceback
    
    tests = [
        ("Colorbar label configuration", test_colorbar_label_configuration),
        ("Title font size increased", test_title_font_size_increased),
        ("No regressions", test_no_regressions),
        ("Comment font unchanged", test_comment_font_unchanged),
    ]
    
    print("=" * 70)
    print("Testing Spectrogram UI Improvements")
    print("=" * 70)
    
    failed = []
    for test_name, test_func in tests:
        try:
            print(f"\nRunning: {test_name}...")
            test_func()
        except Exception as e:
            print(f"✗ FAILED: {e}")
            traceback.print_exc()
            failed.append(test_name)
    
    print("\n" + "=" * 70)
    if failed:
        print(f"FAILED: {len(failed)} test(s) failed")
        for name in failed:
            print(f"  - {name}")
        sys.exit(1)
    else:
        print("SUCCESS: All tests passed!")
        sys.exit(0)
