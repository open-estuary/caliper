#include <linux/module.h>
#include <linux/vermagic.h>
#include <linux/compiler.h>

MODULE_INFO(vermagic, VERMAGIC_STRING);

__visible struct module __this_module
__attribute__((section(".gnu.linkonce.this_module"))) = {
	.name = KBUILD_MODNAME,
	.init = init_module,
#ifdef CONFIG_MODULE_UNLOAD
	.exit = cleanup_module,
#endif
	.arch = MODULE_ARCH_INIT,
};

static const struct modversion_info ____versions[]
__used
__attribute__((section("__versions"))) = {
	{ 0x2b22e0c3, __VMLINUX_SYMBOL_STR(module_layout) },
	{ 0xce814a29, __VMLINUX_SYMBOL_STR(remove_proc_entry) },
	{ 0x730dfaae, __VMLINUX_SYMBOL_STR(dummy_func_test) },
	{ 0x9bbd3844, __VMLINUX_SYMBOL_STR(proc_mkdir) },
};

static const char __module_depends[]
__used
__attribute__((section(".modinfo"))) =
"depends=dummy_del_mod";


MODULE_INFO(srcversion, "7CF79F4F53DC98F1A733283");
