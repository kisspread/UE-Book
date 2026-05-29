# Text 3D

> Tool to create 3D Text with advanced options

| 属性 | 值 |
|---|---|
| 中文名 | 三维文本工具 |
| 分类 | Text |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质、字体资产） |
| 模块 | `Text3D` (Runtime), `Text3DEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-09-03 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Text3D) | |

## 用途

Text3D 插件专为虚拟制片（Virtual Production）设计，用于在 UE5 场景中生成具有高级选项的 3D 文本。它解决了传统 2D 文本在 3D 空间中缺乏深度、材质和物理交互能力的问题。该插件基于 `GeometryProcessing` 和 `GeometryScripting` 等底层几何处理插件，能够将文本轮廓转换为可编辑、可渲染的 3D 网格，并支持丰富的排版和材质控制。

## 使用场景

- **虚拟制片与动态图形（Motion Design）**：在 LED 虚拟影棚或实时渲染流程中，快速创建和编辑 3D 标题、字幕或信息标签。
- **游戏 UI 与 HUD**：为游戏内界面创建具有深度、光照和动画效果的立体文字元素。
- **建筑可视化与产品展示**：在展示场景中，添加空间感强烈的立体文字标注、标题或品牌名称。
- **动态内容生成**：根据运行时数据（如玩家名称、得分）程序化地生成 3D 文字。

## 蓝图用法

Text3D 插件提供了用于创建和配置 3D 文本的核心蓝图类。其功能主要通过 `UText3DComponent` 和相关资产进行控制。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 创建 Text3D 组件 | 在 Actor 上添加一个 3D 文本组件 | `UText3DComponent` |
| 设置文本内容 | 设置要显示的字符串 | `UText3DComponent` |
| 设置字体 | 指定用于生成网格的字体资产 | `UText3DComponent` |
| 调整样式 | 控制斜面、挤出、材质等外观参数 | `UText3DComponent` |

**使用示例**：在蓝图中，你可以向一个 Actor 添加 `Text3DComponent`，然后通过该组件的属性节点设置文本字符串、选择字体，并通过材质实例动态调整文字的颜色和金属感。

## C++ 用法

### 头文件引入

```cpp
#include "Text3DComponent.h"
#include "Text3DTypes.h" // 用于访问样式枚举等
```

### 基本用法

从测试用例和源码推断，以下是 C++ 中创建和配置 3D 文本的基本流程：

```cpp
// 创建一个文本 3D 组件
UText3DComponent* Text3DComp = NewObject<UText3DComponent>(MyActor);
Text3DComp->RegisterComponent();
Text3DComp->AttachToComponent(MyActor->GetRootComponent(), FAttachmentTransformRules::KeepRelativeTransform);

// 设置文本内容
Text3DComp->SetText(FText::FromString(TEXT("Hello UE5!")));

// 设置字体 (需要有效的 UFont 或 UText3DFont 资产)
Text3DComp->SetFont(MyFontAsset);

// 设置基础样式
Text3DComp->SetExtrude(5.0f); // 设置挤出深度
Text3DComp->SetBevel(1.0f);   // 设置斜面大小
```

*（注意：具体 API 可能因插件版本而异，请参考源码中的 `UText3DComponent` 类声明。）*

### 进阶用法

可以通过 `Text3D` 模块中的高级参数控制文本的几何生成过程，例如细分级别、倒角类型以及材质通道分配。`Text3DEditor` 模块则提供了在编辑器中交互式编辑这些参数的框架。

## Demo 示例

由于这是一个汇总页，具体的、可编译的最小 C++ 和蓝图示例，请参阅各子模块的文档：
- [**Text3D 模块文档**](Text3D.md)（运行时核心功能示例）
- [**Text3DEditor 模块文档**](Text3DEditor.md)（编辑器集成示例）

## 模块依赖

要使用 Text3D 插件，你的项目或模块需要依赖以下**独特**的模块：

| 模块 | 用途 |
|---|---|
| `FreeType2` | 用于解析字体文件，提取字形轮廓。 |
| `HarfBuzz` | 高级文本排版引擎，处理复杂的文本布局（如阿拉伯文、印地文）。 |
| `GeometryProcessing` | 提供核心的几何操作算法，用于将 2D 轮廓转换为 3D 网格。 |
| `GeometryScripting` | 为几何操作提供蓝图/脚本友好的接口。 |
| `DirectX` (仅 Text3DEditor) | 编辑器模块可能依赖 DirectX 进行特定的预览或计算。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `660d059d` | Text3D: Text3D relies on GeometryMask for its material functions (content-only dependency). | Text3D 材质功能现在依赖 GeometryMask 插件（仅为内容依赖）。 |
| 2026-05-22 | `f3f717af` | Text3D: fix build errors when building with server (no free type) | 修复了在无 FreeType 的服务器环境下构建时出现的错误。 |
| 2026-05-21 | `14da3adf` | Text3D: fixed issue where in the exact timing where preparation of Text3D only held onto new glyph h | 修复了一个在特定时序下，文本准备过程仅持有新字形数据的边缘问题。 |
| 2026-05-15 | `2f367c6e` | Text3D: fix function defined in editor-only | 修复了某个仅在编辑器中定义的函数。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 为 Text3D 和形状添加了项目设置，可强制禁用其碰撞。 |

### 维护评价

- **活跃维护**：该插件最近一次实质性更新（几何依赖、构建修复）距今不足一个月，维护非常活跃。
- **项目背景**：作为 Epic “Motion Design” 项目的一部分，它专注于虚拟制片流程，享有持续的开发关注。
- **状态**：插件已从 Experimental 正式迁移至 VirtualProduction 目录，表明其进入相对稳定阶段。
- **建议**：推荐在需要运行时或编辑器中生成高质量 3D 文本的虚拟制片、游戏或可视化项目中使用。鉴于其依赖链（FreeType, HarfBuzz, GeometryProcessing），需注意项目包体大小和构建复杂度。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Text3D)
- [Text3D 模块文档](Text3D.md)
- [Text3DEditor 模块文档](Text3DEditor.md)
- *(暂无官方独立文档)*