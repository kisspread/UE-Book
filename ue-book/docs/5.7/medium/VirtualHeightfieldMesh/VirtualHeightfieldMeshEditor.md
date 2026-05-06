# Virtual Heightfield Mesh

> Mesh renderer for virtual texture heightfields

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟高度场网格 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资源、HeightfieldMinMaxTexture 资产类型） |
| 模块 | `VirtualHeightfieldMesh` (Runtime), `VirtualHeightfieldMeshEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualHeightfieldMesh) | |

## 用途

Virtual Heightfield Mesh 是一个实验性插件，用于将虚拟纹理（Runtime Virtual Texture）的高度场数据渲染为网格几何体。它通过分析虚拟纹理的 MinMax 高度信息，生成低 LOD 的网格表示，适用于大世界地形、远景简化等场景。该插件仍处于早期开发阶段，仅提供基础编辑器工具和运行时组件。

## 使用场景

- **优化大型地形渲染**：将高精度虚拟纹理高度场转换为轻量网格，用于远距离或低重要性区域。
- **World Partition 构建优化**：通过自动化工具在 World Partition 构建过程中生成虚拟高度场网格。
- **编辑器可视化**：提供细节面板定制、缩略图显示和一步构建 MinMax 纹理的功能。

## 蓝图用法

本插件主要为编辑器提供工具，运行时模块 `VirtualHeightfieldMesh` 提供蓝图可调用的组件和函数。由于未能获取运行时模块源码，以下仅列出编辑器模块中可能通过蓝图间接使用的功能。

| 节点 | 说明 | 所在类 |
|---|---|---|
| （暂无公开可调用的蓝图节点） | | |

> 编辑器模块 `VirtualHeightfieldMeshEditor` 不暴露任何 BlueprintCallable 函数。运行时组件 `UVirtualHeightfieldMeshComponent` 的函数请参考运行时模块文档。

## C++ 用法

### 头文件引入

```cpp
#include "VirtualHeightfieldMeshEditorModule.h"
```

### 基本用法

通过 `IVirtualHeightfieldMeshEditorModule` 接口检查组件是否具有 MinMax 纹理并执行构建。

```cpp
#include "VirtualHeightfieldMeshEditorModule.h"
#include "Components/VirtualHeightfieldMeshComponent.h" // 假设运行时头文件路径

void ExampleUsage(UVirtualHeightfieldMeshComponent* Component)
{
    IVirtualHeightfieldMeshEditorModule& EditorModule = FModuleManager::LoadModuleChecked<IVirtualHeightfieldMeshEditorModule>("VirtualHeightfieldMeshEditor");
    
    // 检查是否已有 MinMax 纹理
    if (!EditorModule.HasMinMaxHeightTexture(Component))
    {
        // 构建 MinMax 纹理
        EditorModule.BuildMinMaxHeightTexture(Component);
    }
}
```

### 进阶用法

使用编辑器细节定制中的内置按钮，或通过 World Partition 构建器自动处理。

```cpp
// 在自定义工具中触发构建
#include "HeightfieldMinMaxTextureBuild.h"

if (VirtualHeightfieldMesh::HasMinMaxHeightTexture(MyComponent))
{
    VirtualHeightfieldMesh::BuildMinMaxHeightTexture(MyComponent);
}
```

## Demo 示例

以下示例展示了如何在 C++ 编辑器模块中集成虚拟高度场网格的构建功能。

**MyHeightfieldTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "HeightfieldMinMaxTextureBuild.h"

class FMyHeightfieldTool
{
public:
    static void BuildForComponent(class UVirtualHeightfieldMeshComponent* Component);
};
```

**MyHeightfieldTool.cpp**
```cpp
#include "MyHeightfieldTool.h"
#include "Components/VirtualHeightfieldMeshComponent.h"

void FMyHeightfieldTool::BuildForComponent(UVirtualHeightfieldMeshComponent* Component)
{
    if (Component && VirtualHeightfieldMesh::HasMinMaxHeightTexture(Component))
    {
        VirtualHeightfieldMesh::BuildMinMaxHeightTexture(Component);
    }
}
```

## 模块依赖

在 `Build.cs` 中将 `VirtualHeightfieldMeshEditor` 添加到依赖中会自动引入其依赖项。以下为编辑器模块独特的依赖，常见编辑器模块（UnrealEd、PropertyEditor 等）不列。

| 模块 | 用途 |
|---|---|
| `WorldPartition` | 支持 World Partition 构建器 |
| `VirtualHeightfieldMesh` | 依赖运行时模块的组件和纹理定义 |
| `AssetTools` | 资产类型动作注册 |
| `UnrealEd` | 工厂、缩略图渲染等编辑器基础 |

> 若仅使用运行时模块，只需依赖 `VirtualHeightfieldMesh`。

## 维护状态

### 近期更新

- 2025-08-29 32884de — 更改 RHICreateTexture 的用法至 RHICmdList.CreateTexture
- 2025-07-18 462ec4e — 修复 V623 警告：临时对象创建和内存泄漏
- 2025-06-18 08316db — 在 MaterialResource 中缓存 ShaderPlatform，从其派生 FeatureLevel
- 2025-04-28 5fe685f — Runtime Virtual Texture 始终使用 PooledRenderTarget，不再使用低级 RHI 纹理
- 2025-04-23 939cc6e — 原始提交：将文件转换为具有 DLL 存储

### 维护评价

- 插件创建于 2025 年 4 月，距今不足半年，处于早期实验阶段。
- 更新内容以底层 API 迁移和修复警告为主，仍处于活跃开发中。
- 目前无重大功能更新，但跟随引擎主线变化保持编译正常。
- 由于是实验性插件，接口可能发生重大变更，建议谨慎用于生产项目。
- **推荐用于学习和测试，不建议在正式项目中依赖**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualHeightfieldMesh)
- [运行时模块文档](https://docs.unrealengine.com/5.7/en-US/API/Plugins/VirtualHeightfieldMesh/)（待补充）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualHeightfieldMesh/Tests)（可能不存在）