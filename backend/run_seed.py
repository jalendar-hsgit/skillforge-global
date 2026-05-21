#!/usr/bin/env python
import sys
sys.path.insert(0, '.')

try:
    from seed_all_demo_data import DemoDataSeeder
    seeder = DemoDataSeeder()
    seeder.run()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
