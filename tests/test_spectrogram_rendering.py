"""
Test for spectrogram rendering tweaks in scripts/utils/reporting.py

This test validates the changes made to the spectrogram function:
1. X-axis major tick locator set to 1.0s (instead of 0.5s)
2. X-axis minor tick locator remains at 0.1s
3. Colorbar label changed to "PCEN dB"
4. Colorbar shows explicit ticks at vmin and vmax
"""
import sys
import os
import tempfile
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_spectrogram_code_structure():
    """Verify the spectrogram code contains the expected changes."""
    reporting_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'scripts',
        'utils',
        'reporting.py'
    )
    
    with open(reporting_path, 'r') as f:
        content = f.read()
    
    # Check x-axis major locator is 1.0
    assert 'ax.xaxis.set_major_locator(mticker.MultipleLocator(1.0))' in content, \
        "X-axis major locator should be set to 1.0s"
    
    # Check x-axis minor locator is 0.1
    assert 'ax.xaxis.set_minor_locator(mticker.MultipleLocator(0.1))' in content, \
        "X-axis minor locator should be set to 0.1s"
    
    # Check colorbar label
    assert '"PCEN dB"' in content, \
        'Colorbar label should be "PCEN dB"'
    
    # Check colorbar ticks are set
    assert 'cbar.set_ticks([vmin, vmax])' in content, \
        "Colorbar should set ticks to [vmin, vmax]"
    
    # Check that old values are not present
    assert 'MultipleLocator(0.5)' not in content, \
        "Old x-axis major locator (0.5s) should be removed"
    
    assert '"PCEN energy (a.u.)"' not in content, \
        "Old colorbar label should be removed"


def test_matplotlib_locators():
    """Test that matplotlib locators work as expected."""
    fig, ax = plt.subplots()
    
    # Set locators as in reporting.py
    ax.xaxis.set_major_locator(mticker.MultipleLocator(1.0))
    ax.xaxis.set_minor_locator(mticker.MultipleLocator(0.1))
    
    # Verify locators are set
    major_locator = ax.xaxis.get_major_locator()
    minor_locator = ax.xaxis.get_minor_locator()
    
    assert isinstance(major_locator, mticker.MultipleLocator), \
        "Major locator should be MultipleLocator"
    assert isinstance(minor_locator, mticker.MultipleLocator), \
        "Minor locator should be MultipleLocator"
    
    # Test tick positions on a sample range
    ax.set_xlim(0, 5)
    major_ticks = major_locator.tick_values(0, 5)
    minor_ticks = minor_locator.tick_values(0, 5)
    
    # Major ticks should be at 0, 1, 2, 3, 4, 5
    expected_major = np.array([0, 1, 2, 3, 4, 5])
    major_in_range = major_ticks[(major_ticks >= 0) & (major_ticks <= 5)]
    np.testing.assert_array_almost_equal(
        major_in_range,
        expected_major,
        err_msg="Major ticks should be at whole seconds"
    )
    
    # Minor ticks should include 0.1, 0.2, ..., 0.9, 1.1, etc.
    assert any(np.isclose(minor_ticks, 0.1)), \
        "Minor ticks should include sub-second intervals"
    
    plt.close(fig)


def test_colorbar_ticks():
    """Test colorbar tick configuration."""
    fig, ax = plt.subplots()
    
    # Create a simple image
    data = np.random.rand(10, 10)
    img = ax.imshow(data, cmap='plasma')
    
    # Create colorbar
    cbar = fig.colorbar(img)
    
    # Set ticks to vmin/vmax as in reporting.py
    vmin, vmax = img.get_clim()
    cbar.set_ticks([vmin, vmax])
    
    # Verify ticks are set
    ticks = cbar.get_ticks()
    assert len(ticks) == 2, "Colorbar should have 2 ticks"
    assert np.isclose(ticks[0], vmin), "First tick should be vmin"
    assert np.isclose(ticks[1], vmax), "Second tick should be vmax"
    
    plt.close(fig)


if __name__ == '__main__':
    import traceback
    
    tests = [
        ("Code structure", test_spectrogram_code_structure),
        ("Matplotlib locators", test_matplotlib_locators),
        ("Colorbar ticks", test_colorbar_ticks),
    ]
    
    print("=" * 70)
    print("Testing Spectrogram Rendering Tweaks")
    print("=" * 70)
    
    failed = []
    for test_name, test_func in tests:
        try:
            print(f"\nRunning: {test_name}...", end=" ")
            test_func()
            print("✓ PASSED")
        except Exception as e:
            print(f"✗ FAILED")
            print(f"  Error: {e}")
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
