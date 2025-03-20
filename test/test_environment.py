import subprocess
import pkg_resources
from pathlib import Path


def test_environment_matches_requirements(requirements_path="requirements.txt"):
    """
    Test if the current environment's packages match those in requirements.txt.
    Compares package names and versions, ignoring case and any whitespace.
    """
    # Get the requirements.txt content
    req_path = Path(requirements_path)
    if not req_path.exists():
        raise FileNotFoundError("requirements.txt not found")

    with open(req_path) as f:
        requirements = f.read().strip().split("\n")

    # Clean requirements (remove empty lines and comments)
    requirements = [r.strip() for r in requirements if r.strip() and not r.startswith("#")]

    # Get current environment packages using pip freeze
    result = subprocess.run(["pip", "freeze"], capture_output=True, text=True)
    installed = result.stdout.strip().split("\n")

    # Convert both lists to sets of (name, version) tuples for comparison
    def parse_requirement(req):
        try:
            req_obj = pkg_resources.Requirement.parse(req)
            return (req_obj.name.lower(), str(req_obj.specifier))
        except:
            return None

    required_pkgs = {parse_requirement(req) for req in requirements if parse_requirement(req)}
    installed_pkgs = {parse_requirement(pkg) for pkg in installed if parse_requirement(pkg)}

    # Find missing and extra packages
    missing_pkgs = required_pkgs - installed_pkgs
    extra_pkgs = installed_pkgs - required_pkgs

    # Prepare error message if there are discrepancies
    error_msg = []
    if missing_pkgs:
        error_msg.append("Missing packages:")
        error_msg.extend(f"  - {name}{version}" for name, version in missing_pkgs)

    if extra_pkgs:
        if error_msg:
            error_msg.append("")
        error_msg.append("Extra packages installed:")
        error_msg.extend(f"  - {name}{version}" for name, version in extra_pkgs)

    # Assert no discrepancies
    assert not error_msg, "\n".join(error_msg)


if __name__ == "__main__":
    try:
        test_environment_matches_requirements()
        print("✅ Environment matches requirements.txt")
    except AssertionError as e:
        print("❌ Environment check failed:")
        print(str(e))
    except FileNotFoundError:
        print("❌ Error: requirements.txt not found")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
