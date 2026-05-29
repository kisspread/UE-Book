# Virtual Heightfield Mesh

> Mesh renderer for virtual texture heightfields

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟高度场网格 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `VirtualHeightfieldMesh` (Runtime), `VirtualHeightfieldMeshEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-22 |
| 年龄标签 | 🏛️ 文物（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualHeightfieldMesh) | |

## 用途

VirtualHeightfieldMesh 是一个**基于虚拟纹理的高度场网格渲染器**。它解决了大地形渲染中的性能与精度问题：

- **核心原理**：将地形高度信息编码到虚拟纹理（Virtual Texture）中，利用虚拟纹理的流式加载机制，根据相机距离动态加载不同精度的高度数据
- **MinMax 纹理**：为虚拟纹理生成层级式高度范围纹理（Min/Max Height Texture），用于快速剔除不可见的地形区域，是性能优化的关键
- **优势**：相比传统固定 LOD 网格，可以实现更平滑的 LOD 过渡和更低的内存占用，特别适合超大世界场景

**为什么存在**：UE5 的虚拟纹理系统本身只支持 2D 纹理流式，这个插件将其扩展到 3D 地形高度场，使得地形网格的几何细节也能按需流式加载。

## 使用场景

- 你正在制作超大开放世界，地形面积达到数十平方公里 → 用 VirtualHeightfieldMesh 实现高效地形渲染
- 你需要地形在近处显示极高细节（如山崖裂缝），远处则大幅简化 → 利用虚拟纹理的 Mip 流式机制自动处理
- 你使用 World Partition 管理大世界，需要地形 LOD 也能流式管理 → 此插件集成了 World Partition Builder

## 蓝图用法

### 核心组件

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UVirtualHeightfieldMeshComponent` | 虚拟高度场网格组件，附加到 Actor 上渲染地形 | `UVirtualHeightfieldMeshComponent` |

### 编辑器操作

通过组件的 Details 面板可以执行以下操作：

| 操作 | 说明 |
|---|---|
| **Set Bounds** | 根据虚拟纹理自动设置组件包围盒 |
| **Build MinMax Texture** | 为当前组件构建 MinMax 高度纹理 |
| **Refresh Thumbnail** | 刷新虚拟纹理缩略图预览 |

### 使用示例

1. 在场景中放置一个 Actor，添加 `UVirtualHeightfieldMeshComponent`
2. 在组件属性中指定 Runtime Virtual Texture 和虚拟纹理资产
3. 点击 **Set Bounds** 自动计算包围盒
4. 点击 **Build MinMax Texture** 生成层级高度范围纹理
5. 分配合适的材质（使用 VT 采样节点读取高度数据）

## C++ 用法

### 头文件引入

```cpp
#include "VirtualHeightfieldMesh/Public/VirtualHeightfieldMeshModule.h"
```

### 基本用法

检查组件是否已有 MinMax 高度纹理，并构建纹理（来自编辑器模块）：

```cpp
#include "VirtualHeightfieldMesh/Public/VirtualHeightfieldMeshComponent.h"
#include "VirtualHeightfieldMeshEditor/Public/VirtualHeightfieldMeshEditorModule.h"

// 获取编辑器模块接口
IVirtualHeightfieldMeshEditorModule& EditorModule = 
    FModuleManager::GetModuleChecked<IVirtualHeightfieldMeshEditorModule>("VirtualHeightfieldMeshEditor");

// 检查组件是否有 MinMax 纹理
if (EditorModule.HasMinMaxHeightTexture(MyComponent))
{
    UE_LOG(LogTemp, Log, TEXT("Component already has MinMax height texture"));
}
else
{
    // 构建 MinMax 高度纹理
    bool bSuccess = EditorModule.BuildMinMaxHeightTexture(MyComponent);
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("MinMax height texture built successfully"));
    }
}
```

来源：`Public/VirtualHeightfieldMeshEditorModule.h`

### 进阶用法

使用命名空间中的辅助函数（在编辑器/Commandlet 环境中）：

```cpp
#include "VirtualHeightfieldMesh/Private/HeightfieldMinMaxTextureBuild.h"

// 直接使用命名空间函数（内部实现）
if (VirtualHeightfieldMesh::HasMinMaxHeightTexture(MyComponent))
{
    // 仅在需要重建时调用
    VirtualHeightfieldMesh::BuildMinMaxHeightTexture(MyComponent);
}
```

来源：`Private/HeightfieldMinMaxTextureBuild.h`

## Demo 示例

创建一个带有虚拟高度场网格的 Actor：

```cpp
// VirtualHeightfieldMeshDemoActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "VirtualHeightfieldMeshDemoActor.generated.h"

class UVirtualHeightfieldMeshComponent;
class URuntimeVirtualTexture;

UCLASS()
class AVirtualHeightfieldMeshDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AVirtualHeightfieldMeshDemoActor();

    /** 设置虚拟纹理资产并刷新组件 */
    UFUNCTION(BlueprintCallable, Category = "Virtual Heightfield")
    void SetVirtualTexture(URuntimeVirtualTexture* InVirtualTexture);

    /** 重新构建 MinMax 高度纹理（仅编辑器） */
    UFUNCTION(BlueprintCallable, Category = "Virtual Heightfield")
    bool RebuildMinMaxHeightTexture();

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    UVirtualHeightfieldMeshComponent* HeightfieldComponent;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Virtual Heightfield")
    URuntimeVirtualTexture* VirtualTextureAsset;
};
```

```cpp
// VirtualHeightfieldMeshDemoActor.cpp
#include "VirtualHeightfieldMeshDemoActor.h"
#include "VirtualHeightfieldMeshComponent.h"

AVirtualHeightfieldMeshDemoActor::AVirtualHeightfieldMeshDemoActor()
{
    HeightfieldComponent = CreateDefaultSubobject<UVirtualHeightfieldMeshComponent>(
        TEXT("HeightfieldMesh"));
    RootComponent = HeightfieldComponent;
}

void AVirtualHeightfieldMeshDemoActor::SetVirtualTexture(URuntimeVirtualTexture* InVirtualTexture)
{
    VirtualTextureAsset = InVirtualTexture;
    if (HeightfieldComponent)
    {
        HeightfieldComponent->SetRuntimeVirtualTexture(InVirtualTexture);
    }
}

bool AVirtualHeightfieldMeshDemoActor::RebuildMinMaxHeightTexture()
{
#if WITH_EDITOR
    IVirtualHeightfieldMeshEditorModule* EditorModule = 
        FModuleManager::GetModulePtr<IVirtualHeightfieldMeshEditorModule>(
            "VirtualHeightfieldMeshEditor");
    
    if (EditorModule && HeightfieldComponent)
    {
        return EditorModule->BuildMinMaxHeightTexture(HeightfieldComponent);
    }
#endif
    return false;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RenderCore` | 底层渲染核心功能 |
| `RHI` | 渲染硬件接口，用于纹理创建 |
| `VirtualTexture` | 虚拟纹理系统核心 |
| `Landscape` | 地形系统集成 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新的 UE_LOGF 格式 |
| 2026-03-05 | `1adb9f68` | New material translator work: | 材质翻译器重构相关改动 |
| 2026-02-03 | `61433296` | Rename FViewMatrices members to follow the <Source>To<Target> pattern for transforms, to reduce ambi | 视图矩阵成员重命名以统一变换命名规范 |
| 2026-01-07 | `57ff2f55` | Deprecate legacy GPU profiler related macros. | 废弃旧版 GPU 性能分析相关宏 |
| 2025-08-29 | `32884de4` | Changing more uses of RHICreateTexture to RHICmdList.CreateTexture. | 将 RHI 纹理创建迁移到命令列表模式 |

### 维护评价

**维护状态：活跃维护中**

- 插件创建于 2020 年，已有约 6 年历史
- 近期（2026 年）仍有持续的代码维护和引擎 API 适配更新
- 更新主要是跟随引擎架构演进（RHI 命令列表化、日志宏标准化、矩阵命名规范化等），说明插件仍在被引擎团队关注
- 但**仍是实验性状态**（`IsExperimentalVersion=true`，`EnabledByDefault=false`），API 可能在未来版本发生变化
- 6 年未出实验状态，表明该功能的稳定化优先级可能不高

⚠️ **使用注意**：此插件目前仍标记为实验性，生产环境使用需谨慎，建议做好 API 变更的应对准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualHeightfieldMesh)
- [官方文档](https://docs.unrealengine.com/)（暂无专用文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualHeightfieldMesh/Tests)（如存在）