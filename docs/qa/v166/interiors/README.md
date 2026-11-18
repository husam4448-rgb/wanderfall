# V166 — actual Android interior QA (non-release)

Captured from a running Android emulator, not an image concept or manually edited game screenshot.

- **Workflow:** [V166 run 44379514829](https://github.com/husam4448-rgb/wanderfall/actions/runs/44379514829)
- **Commit under test:** `1d38f80a3481c152abcc2f10babb7f8bf2ab6eb5`
- **Status:** Source regression, immutable-character checks, Android Java compilation, test-package assembly, actual Android launch, and eight indoor screenshot captures passed.
- The camera/scene switches are temporary QA-only instrumentation compiled into a separate test application, never into production gameplay.

The numbered JPEG files cover apartments, offices, market, hotel, school, factory, warehouse, and residences at an actual V163 seed-generated interior. Each retains the original characters and active entrance.

**Observed:** Specific authored materials now replace outdoor-gravel-looking floors; texture repeat scale reduced; authentic storage icons replace most generic square containers; furniture appearance unchanged except full industrial collision fitting.

**Not approved:** Some rooms have too little collidable furniture; partition walls, doors, and miscellaneous fixed props still have geometric artwork. These captures do not certify every indoor location, all world seeds, interactions, or the release.
