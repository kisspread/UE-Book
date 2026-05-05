# ZoneGraphEditor — 编辑器模块

> 提供 ZoneGraph 的编辑器端功能：形状可视化器、属性面板自定义、编辑器样式。

## 模块概览

| 属性 | 值 |
|---|---|
| 模块名 | `ZoneGraphEditor` |
| 类型 | Editor |
| 加载阶段 | PostEngineInit |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ZoneGraph/Source/ZoneGraphEditor) | |

## 依赖

### PublicDependencyModuleNames

| 模块 | 用途 |
|---|---|
| `ZoneGraph` | 运行时核心 |
| `UnrealEd` | 编辑器框架 |
| `PropertyEditor` | 属性编辑器 |
| `ComponentVisualizers` | 组件可视化器 |
| `DetailCustomizations` | Detail 面板自定义 |
| `AssetTools` | 资产工具 |
| `Slate/SlateCore` | UI 框架 |
| `LevelEditor` | 关卡编辑器 |
| `InputCore` | 输入核心 |

### PrivateDependencyModuleNames

| 模块 | 用途 |
|---|---|
| `RenderCore` | 渲染核心 |
| `AIGraph` | AI 图形编辑器 |
| `ToolMenus` | 工具菜单 |
| `Projects` | 项目信息 |

## 关键功能

### 形状可视化器

`ZoneShapeComponentVisualizer` 提供 `UZoneShapeComponent` 在编辑器视口中的可视化：
- 绘制形状点和连接线
- 绘制 Bezier 控制手柄
- 支持交互式编辑（拖拽点、添加/删除点）

### 属性面板自定义

模块注册了大量 Detail Customization，为各种类型提供自定义的属性面板：

| 类 | 说明 |
|---|---|
| `ZoneShapeComponentDetails` | 形状组件 Detail 面板 |
| `ZoneGraphTagDetails` | 标签选择器 |
| `ZoneGraphTagFilterDetails` | 标签过滤器面板 |
| `ZoneGraphTagInfoDetails` | 标签信息面板 |
| `ZoneGraphTagMaskDetails` | 标签掩码面板 |
| `ZoneGraphTessellationSettingsDetails` | 细分设置面板 |
| `ZoneLaneDescDetails` | 车道描述面板 |
| `ZoneLaneProfileDetails` | 车道配置面板 |
| `ZoneLaneProfileRefDetails` | 车道配置引用面板 |

### 编辑器样式

`ZoneGraphEditorStyle` 提供编辑器图标和样式资源。

### 属性工具

`ZoneGraphPropertyUtils` 提供属性编辑的通用工具函数。

## 文件列表

| 文件 | 说明 |
|---|---|
| `ZoneShapeComponentVisualizer.h/cpp` | 形状组件可视化器 |
| `ZoneShapeComponentDetails.h/cpp` | 形状组件 Detail 面板 |
| `ZoneGraphTagDetails.h/cpp` | 标签选择器 |
| `ZoneGraphTagFilterDetails.h/cpp` | 标签过滤器面板 |
| `ZoneGraphTagInfoDetails.h/cpp` | 标签信息面板 |
| `ZoneGraphTagMaskDetails.h/cpp` | 标签掩码面板 |
| `ZoneGraphTessellationSettingsDetails.h/cpp` | 细分设置面板 |
| `ZoneLaneDescDetails.h/cpp` | 车道描述面板 |
| `ZoneLaneProfileDetails.h/cpp` | 车道配置面板 |
| `ZoneLaneProfileRefDetails.h/cpp` | 车道配置引用面板 |
| `ZoneGraphEditorStyle.h/cpp` | 编辑器样式 |
| `ZoneGraphPropertyUtils.h/cpp` | 属性工具 |
| `ZoneGraphEditorModule.h/cpp` | 模块实现 |
| `IZoneGraphEditor.h` | 模块接口 |
