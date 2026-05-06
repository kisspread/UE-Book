# UAF Control Rig

> Control Rig integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF 控制绑定集成 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFControlRig` (Runtime), `UAFControlRigEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-07-22 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFControlRig) | |

## 总体用途

将 Unreal Animation Framework（UAF）集成到 Control Rig 系统中，使 Control Rig 资产能够继承 `IControlRigAssetInterface`，并支持 UAF 特性（如特征（Trait）映射、延迟针脚处理等）。解决 Control Rig 与 UAF 之间的数据交互与执行协同问题。

## 模块列表

| 模块 | 类型 | 一句话说明 | 文档 |
|---|---|---|---|
| `UAFControlRig` | Runtime | 核心运行时模块，提供 UAF 相关的 Control Rig 节点、特征映射及构造执行逻辑 | [UAFControlRig.md](./UAFControlRig.md) |
| `UAFControlRigEditor` | Runtime | 编辑器模块，提供 UAF Control Rig 资产的编辑器支持与 UI 集成 | [UAFControlRigEditor.md](./UAFControlRigEditor.md) |

> 注：`UAFControlRigEditor` 虽然是 Runtime 类型（非 UncookedOnly），但通常仅在编辑器中使用。

## 使用场景

- 你需要在 Control Rig 中使用 UAF 的特征（Trait）系统来驱动角色动画。
- 你正在开发基于 UAF 的动画框架，并希望 Control Rig 资产能原生支持 UAF 接口。
- 你需要处理 Control Rig 中延迟针脚（latent pins）的顺序问题，并利用 UAF 的映射控制初始化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFControlRig)
- 暂无官方文档（`DocsURL` 为空）
- 测试用例：未提供（可通过插件源码内 `Tests` 目录或引擎全局测试文件寻找）