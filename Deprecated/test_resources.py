"""
Test script for Resource Manager
Run with: python test_resources.py
"""

from chforge.resources import ResourceConfig, ResourceManager

print('=' * 60)
print('1. GENERATE PROFILES (threads=[2,4,8], memory=[2G,4G])')
print('=' * 60)
profiles = ResourceManager.generate_profiles(
    threads=[2, 4, 8],
    memory=['2G', '4G']
)
for p in profiles:
    print(f'  {p}')

print()
print('=' * 60)
print('2. PRESET: MEDIUM')
print('=' * 60)
for p in ResourceManager.preset_medium():
    print(f'  {p}')

print()
print('=' * 60)
print('3. PRESET: QUICK')
print('=' * 60)
for p in ResourceManager.preset_quick():
    print(f'  {p}')

print()
print('=' * 60)
print('4. SINGLE CONFIG TO DICT')
print('=' * 60)
config = ResourceConfig(threads=8, memory='8G', execution_time=60)
print(f'  Config: {config}')
print(f'  Settings: {config.to_dict()}')