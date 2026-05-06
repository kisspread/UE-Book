# Virtual Production Roles

> Allows users to manage Virtual Production Role assignment.

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟制片角色管理 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置资源） |
| 模块 | `VPRoles` (Runtime), `VPRolesEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-12 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualProduction/VPRoles) | |

## 总体用途

VPRoles 插件为虚拟制片工作流提供基于角色的控制权限管理。它允许用户定义和分配一系列角色（例如“Director”、“Camera Operator”、“Lighting Tech”），并在整个虚拟制片系统中根据角色来限制或授权特定操作。该插件解决了多用户协作环境下的权限边界问题，确保只有合适的人员能执行关键操作。

## 模块列表

| 模块 | 类型 | 一句话说明 |
|---|---|---|
| `VPRoles` | Runtime | 核心模块，负责角色定义、存储及运行时查询。 |
| `VPRolesEditor` | Runtime | 编辑器扩展，提供角色管理器面板和设置 UI。 |

> 详细 API 与用法参见 [VPRoles.md](./VPRoles.md) 和 [VPRolesEditor.md](./VPRolesEditor.md)。

## 使用场景

- **多用户远程虚拟制片**：为摄影师、灯光师、导演等分配不同角色，自动限制对摄影机、灯光或场景元素的修改权限。
- **复杂权限工作流**：配合其他虚拟制片插件（如 VPUtilities、VPSettings），实现基于角色的自动功能开关。
- **安全性控制**：防止未授权的用户意外修改关键场景元素，降低误操作风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualProduction/VPRoles)
- [VPRoles 模块文档](./VPRoles.md)
- [VPRolesEditor 模块文档](./VPRolesEditor.md)