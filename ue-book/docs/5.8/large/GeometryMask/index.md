# Geometry Mask

> 

| 属性 | 值 |
|---|---|
| 中文名 | 几何遮罩 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质资产、渲染目标） |
| 模块 | `GeometryMask` (Runtime), `GeometryMaskEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/GeometryMask) | |

## 用途

为虚拟制作提供基于几何形状的遮罩系统。该插件允许用户使用任意几何体（Actor）作为遮罩形状，将遮罩信息写入渲染目标（Render Target），供后处理材质或其他视觉效果读取使用。核心功能包括：

- **遮罩写入器（Mask Writer）**：将 Actor 组件的几何形状转换为遮罩数据，与具体遮罩逻辑解耦
- **渲染目标切片管理**：支持 Render Target Slice 索引，允许在同一张 RT 上存储多个遮罩
- **材质资产支持**：提供预设的后处理材质，用于读取和应用遮罩效果

该插件从 Experimental 目录迁移到 VirtualProduction 目录，是 Motion Design 虚拟制作工具链的一部分。

## 使用场景

- 你需要在虚拟制作中用几何体形状控制屏幕区域的可见性 → 用 GeometryMask 创建遮罩
- 你需要在一个渲染目标上存储多个遮罩层 → 用 Render Target Slice 索引管理
- 你需要将遮罩逻辑与 Actor 组件解耦以便复用 → 用 Mask Writer 组件

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [GeometryMask](GeometryMask.md) | Runtime | 核心遮罩运行时逻辑，包含遮罩写入、渲染目标管理、材质接口 |
| [GeometryMaskEditor](GeometryMaskEditor.md) | Editor | 编辑器扩展，提供遮罩配置 UI、材质预览和编辑器集成 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/GeometryMask)
- [GeometryMask 运行时模块文档](GeometryMask.md)
- [GeometryMaskEditor 编辑器模块文档](GeometryMaskEditor.md)