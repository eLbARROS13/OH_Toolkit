from oh_parser import load_profiles, list_subjects, get_profile, inspect_profile

# Load all OH profiles from your directory
profiles = load_profiles(r"E:\Backup PrevOccupAI_PLUS Data\OH_profiles")

# See how many subjects you have
subjects = list_subjects(profiles)
print(f"Loaded {len(subjects)} subjects")  

# Pick one subject to explore
profile = get_profile(profiles, subjects[0])

# See the structure (like a folder tree)
if profile is not None:
	inspect_profile(profile, max_depth=3)
else:
	raise ValueError(f"No profile found for subject: {subjects[0]}")