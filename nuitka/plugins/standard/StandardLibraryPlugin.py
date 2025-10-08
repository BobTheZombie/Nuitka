#     Copyright 2025, Kay Hayen, mailto:kay.hayen@gmail.com find license text at end of file


"""Standard plugin to make core stdlib modules always available for LPM builds."""

import os

from nuitka import Options
from nuitka.containers.OrderedSets import OrderedSet
from nuitka.importing.Importing import locateModule, makeModuleUsageAttempt
from nuitka.plugins.PluginBase import NuitkaPluginBase
from nuitka.utils.ModuleNames import ModuleName


class NuitkaPluginStandardLibraryCompleteness(NuitkaPluginBase):
    """Ensure core stdlib extension modules are bundled for LPM standalone builds."""

    plugin_name = "standard-library"
    plugin_desc = "Ensure standard library extensions are included for LPM builds."
    plugin_category = "core"

    coreStandardModuleNames = (
        "hashlib",
        "_hashlib",
        "ssl",
        "sqlite3",
        "datetime",
        "_decimal",
        "_struct",
        "binascii",
        "zlib",
        "select",
        "multiprocessing",
        "asyncio",
    )

    @staticmethod
    def isAlwaysEnabled():
        return True

    def __init__(self):
        value = os.environ.get("LPM_MODE")

        if value is None:
            normalized = None
        else:
            normalized = value.strip().lower()

        self.must_include = normalized not in (None, "", "0", "false")
        self.mustInclude = self.must_include

    def onModuleDiscovered(self, module):
        if not self.must_include:
            return

        if not Options.isStandaloneMode():
            return

        if not module.isMainModule():
            return

        try:
            standard_modules = module.standard_library_modules
        except AttributeError:
            return

        if not hasattr(standard_modules, "add"):
            standard_modules = OrderedSet(standard_modules)
            module.standard_library_modules = standard_modules

        existing_names = {usage.module_name for usage in standard_modules}

        for module_name_str in self.coreStandardModuleNames:
            module_name = ModuleName(module_name_str)

            if module_name in existing_names:
                continue

            (
                found_module_name,
                module_filename,
                module_kind,
                finding,
            ) = locateModule(module_name=module_name, parent_package=None, level=0)

            if finding == "not-found" or module_filename is None:
                continue

            standard_modules.add(
                makeModuleUsageAttempt(
                    module_name=found_module_name,
                    filename=module_filename,
                    module_kind=module_kind,
                    finding=finding,
                    level=0,
                    source_ref=module.source_ref,
                    reason="LPM standard library requirement",
                )
            )

            existing_names.add(found_module_name)
            existing_names.add(module_name)


#     Part of "Nuitka", an optimizing Python compiler that is compatible and
#     integrates with CPython, but also works on its own.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
