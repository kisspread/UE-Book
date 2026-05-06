# UAF Mirroring

> Keyframe mirroring for UAF

| 属性 | 值 |
|---|---|
| 中文名 | UAF 镜像 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFMirroring` (Runtime), `UAFMirroringUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFMirroring) | |

## 总体用途

UAF Mirroring 为 Unreal Animation Framework (UAF) 提供关键帧（keyframe）镜像功能。它允许在动画制作过程中，将已有的动画数据（如骨骼变换、属性曲线）沿指定轴向（通常是左右）进行镜像复制，从而快速生成对称的动作，避免手动重复调整。该插件适用于需要大规模制作左右对称动画的管线（如角色移动、攻击动作），显著提升动画生产效率。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `UAFMirroring` | Runtime | 运行时核心模块，提供镜像规则的存储、计算和动画节点接口 |
| `UAFMirroringUncookedOnly` | UncookedOnly | 编辑器（未烘焙）模块，负责镜像数据生成、预览及节点编辑支持 |

> 详细 API 请参阅各模块独立文档：[UAFMirroring.md](./UAFMirroring.md) / [UAFMirroringUncookedOnly.md](./UAFMirroringUncookedOnly.md)

## 使用场景

- **角色动画镜像**：制作角色左右对称的移动、攻击、转身等动画时，只需制作一侧动作，另一侧通过镜像自动生成。
- **动画管线自动化**：在动画导入或重定向流程中批量应用镜像规则，减少人工调整。
- **属性曲线镜像**：不仅支持骨骼变换，还能镜像自定义属性曲线（如表情、变形目标权重），保持整体一致性。

## 维护评价

该插件于 2025 年 8 月创建，仍处于实验阶段。从近期提交（2025-08-20）看，开发团队正在积极修复镜像任务的终止逻辑、优化属性和骨骼的独立跳过功能。作为新插件，功能基础且可能包含未发现的边界情况，但核心能力已可用于生产管线中的部分场景。建议在非关键流程中先行验证。

## 相关链接

- [源码（UAF Mirroring 目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFMirroring)
- [UAF 插件（依赖）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAF)（仅内部参考）