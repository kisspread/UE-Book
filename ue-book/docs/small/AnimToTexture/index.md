# AnimToTexture

> Converts SkeletalMesh Animations into Textures

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | 否（需手动启用） |
| 包含内容 | 是 |
| 模块 | AnimToTexture (Runtime), AnimToTextureEditor (Editor) |
| 创建时间 | 2023-03-09 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AnimToTexture) | |

## 用途

AnimToTexture 是一个 **顶点动画纹理 (Vertex Animation Texture, VAT)** 工具，用于将 SkeletalMesh 的骨骼动画烘焙成纹理，然后在运行时通过材质在 StaticMesh 上回放动画。

核心解决的问题：当你需要在场景中渲染大量相同角色的动画（例如 RTS 游戏中的数百个士兵、人群模拟、草地/树木风吹动画），使用 SkeletalMesh 会消耗大量 CPU 骨骼计算资源。AnimToTexture 通过将动画数据预烘焙到纹理中，运行时完全由 GPU 在材质中计算顶点位置，从而将 CPU 开销降到最低，支持大规模实例化渲染。

## 两种工作模式

### Vertex 模式
- 直接存储每一帧每个顶点的 **位置偏移** 和 **法线**
- 适用于不同拓扑结构的网格
- 纹理较大（需要 Position + Normal 两张纹理）
- 精度更高，效果最好

### Bone 模式（默认）
- 存储每一帧每根骨骼的 **位置** 和 **旋转**，加上每个顶点的 **骨骼权重**
- 适用于共享同一 Skeleton 的多个网格（如同一角色的不同装备 LOD）
- 纹理较小（骨骼数远少于顶点数），支持权重重用
- 推荐用于同一骨架的多个网格

## 使用场景

- **RTS / 大规模战斗**：场景中有成百上千个角色同时播放动画，用 ISMC + Bone/VAT 纹理实现 GPU 驱动渲染
- **人群系统**：大量 NPC 同时播放不同动画（行走、站立、交谈），通过实例化 CustomData 控制每人的动画和帧
- **植被动画**：树木、草地的风吹摇摆动画烘焙为顶点动画
- **LOD 替换**：远处角色用 VAT StaticMesh 替代 SkeletalMesh，大幅减少骨骼计算
- **Niagara 粒子**：将动画烘焙到纹理中，在粒子系统中驱动大量网格实例

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AnimationToTexture` | 将 DataAsset 中配置的动画烘焙到纹理（编辑器专用） | `UAnimToTextureBPLibrary` |
| `ConvertSkeletalMeshToStaticMesh` | 将 SkeletalMesh 转换为 StaticMesh（编辑器专用） | `UAnimToTextureBPLibrary` |
| `SetLightMapIndex` | 设置 StaticMesh 的 LightMap UV 通道（编辑器专用） | `UAnimToTextureBPLibrary` |
| `UpdateMaterialInstanceFromDataAsset` | 根据 DataAsset 配置更新材质实例参数（编辑器专用） | `UAnimToTextureBPLibrary` |

### 运行时播放节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetupInstancedMeshComponent` | 初始化 ISMC，分配 CustomData 空间 | `UAnimToTextureInstancePlaybackLibrary` |
| `BatchUpdateInstancesAutoPlayData` | 批量更新所有实例的变换和自动播放数据 | `UAnimToTextureInstancePlaybackLibrary` |
| `BatchUpdateInstancesFrameData` | 批量更新所有实例的变换和帧数据（手动控制） | `UAnimToTextureInstancePlaybackLibrary` |
| `UpdateInstanceAutoPlayData` | 更新单个实例的自动播放数据 | `UAnimToTextureInstancePlaybackLibrary` |
| `UpdateInstanceFrameData` | 更新单个实例的帧数据 | `UAnimToTextureInstancePlaybackLibrary` |
| `GetAutoPlayDataFromDataAsset` | 从 DataAsset 获取指定动画的 AutoPlayData | `UAnimToTextureInstancePlaybackLibrary` |
| `GetFrameDataFromDataAsset` | 从 DataAsset 获取指定动画在指定时间的 FrameData | `UAnimToTextureInstancePlaybackLibrary` |
| `GetFrame` | 根据时间计算当前帧号 | `UAnimToTextureInstancePlaybackLibrary` |

### 蓝图烘焙工作流

1. **创建 AnimToTextureDataAsset**：右键 Content Browser → Animation → AnimToTexture DataAsset
2. **配置 DataAsset**：
   - 指定 `SkeletalMesh`（源骨骼网格）
   - 指定 `StaticMesh`（目标静态网格，先用 `ConvertSkeletalMeshToStaticMesh` 转换）
   - 选择 `Mode`（Bone 或 Vertex）
   - 在 `AnimSequences` 数组中添加要烘焙的动画
   - 设置纹理分辨率和精度
   - 指定输出纹理资产（Position/Normal 或 BonePosition/BoneRotation/BoneWeight）
3. **执行烘焙**：在蓝图中调用 `AnimationToTexture` 节点，传入 DataAsset
4. **配置材质**：调用 `UpdateMaterialInstanceFromDataAsset` 更新材质实例参数
5. **运行时播放**：使用 ISMC 节点批量管理实例动画

### 运行时播放示例（蓝图描述）

**自动播放模式**（AutoPlay，使用引擎时间驱动）：

1. 创建 `InstancedStaticMeshComponent`，设置 StaticMesh 为烘焙后的网格
2. 调用 `SetupInstancedMeshComponent`（NumInstances=N, bAutoPlay=true）
3. 调用 `GetAutoPlayDataFromDataAsset` 获取每人的动画数据（可设置不同的 AnimationIndex 和 TimeOffset 实现异步）
4. 调用 `BatchUpdateInstancesAutoPlayData` 一次性更新所有实例

**手动帧控制模式**（FrameData，适合精确控制）：

1. 同上初始化 ISMC
2. 调用 `SetupInstancedMeshComponent`（bAutoPlay=false）
3. 调用 `GetFrameDataFromDataAsset` 传入游戏时间获取帧数据
4. 调用 `BatchUpdateInstancesFrameData` 更新

## C++ 用法

### 头文件引入

```cpp
// 运行时播放（Runtime 模块）
#include "AnimToTextureInstancePlaybackHelpers.h"
#include "AnimToTextureDataAsset.h"

// 编辑器烘焙（Editor 模块，仅 WITH_EDITOR 下可用）
#include "AnimToTextureBPLibrary.h"
```

### 基本用法 — 运行时批量播放

```cpp
// 假设已有 UAnimToTextureDataAsset* DataAsset 和 UInstancedStaticMeshComponent* ISMC

// 1. 初始化实例组件（自动播放模式）
UAnimToTextureInstancePlaybackLibrary::SetupInstancedMeshComponent(ISMC, NumInstances, true);

// 2. 获取动画数据
FAnimToTextureAutoPlayData AutoPlayData;
UAnimToTextureInstancePlaybackLibrary::GetAutoPlayDataFromDataAsset(
    DataAsset,
    0,              // AnimationIndex（第一个动画）
    AutoPlayData,
    0.0f,           // TimeOffset（不同实例可设不同值实现异步）
    1.0f            // PlayRate
);

// 3. 构建每个实例的数据
TArray<FAnimToTextureAutoPlayData> AllAutoPlayData;
TArray<FTransform> AllTransforms;
for (int32 i = 0; i < NumInstances; ++i)
{
    FAnimToTextureAutoPlayData InstanceData = AutoPlayData;
    InstanceData.TimeOffset = FMath::FRandRange(0.0f, 10.0f); // 随机偏移实现异步
    AllAutoPlayData.Add(InstanceData);
    AllTransforms.Add(FTransform(FRotator::ZeroRotator, FVector(i * 100.f, 0, 0)));
}

// 4. 批量更新
UAnimToTextureInstancePlaybackLibrary::BatchUpdateInstancesAutoPlayData(
    ISMC, AllAutoPlayData, AllTransforms, true);
```

### 手动帧控制

```cpp
// 获取某动画在当前时间的帧数据
FAnimToTextureFrameData FrameData;
UAnimToTextureInstancePlaybackLibrary::GetFrameDataFromDataAsset(
    DataAsset,
    1,              // AnimationIndex（第二个动画）
    GetWorld()->GetTimeSeconds(),
    FrameData,
    0.0f,           // TimeOffset
    1.0f            // PlayRate
);

// 更新单个实例
UAnimToTextureInstancePlaybackLibrary::UpdateInstanceFrameData(ISMC, InstanceIndex, FrameData);
```

## Demo 示例

Plugin 内置了完整的 Mannequin 示例，位于 Content 目录：

| 资产 | 说明 |
|---|---|
| `DA_BoneAnimation` | Bone 模式的 DataAsset 配置 |
| `DA_VertexAnimation` | Vertex 模式的 DataAsset 配置 |
| `BP_AnimToTexture` | 主蓝图，演示烘焙和播放流程 |
| `BP_InstancerAutoPlayData` | AutoPlay 模式的 ISMC 播放示例 |
| `BP_InstancerFrameData` | FrameData 模式的 ISMC 播放示例 |
| `ML_BoneAnimation` / `ML_VertexAnimation` | 材质层，包含 VAT 解码逻辑 |
| `MF_BoneAnimation` / `MF_VertexAnimation` | 材质函数，解包纹理数据 |

## 模块依赖

### AnimToTexture（Runtime 模块）

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（DataAsset、Texture、Mesh 等） |
| `MeshDescription` | 网格数据描述 |

### AnimToTextureEditor（Editor 模块）

| 模块 | 用途 |
|---|---|
| `AnimToTexture` | 依赖 Runtime 模块 |
| `AssetDefinition` | 资产类型定义 |
| `MaterialEditor` | 材质编辑器集成 |
| `MessageLog` | 消息日志输出烘焙状态 |
| `RawMesh` | 原始网格数据操作 |
| `MeshDescription` / `StaticMeshDescription` | 网格描述操作 |
| `ToolMenus` | 编辑器菜单扩展 |
| `UnrealEd` | 编辑器工具函数 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-08-08 | `7213adb` | 新增 SkeletalMesh MeshDescription 函数（标记为未使用） |
| 2025-08-07 | `1aee06f` | 修复 RigidBodies 烘焙问题 |
| 2025-08-06 | `785cdd6` | 修复 API 宏使用 |

### 维护评价

- **状态**：活跃维护
- 创建于 2023 年 3 月，至今约 3 年
- 2025 年 8 月仍有实质性更新（功能新增 + Bug 修复）
- 仍在 Experimental 分类中，API 可能在未来版本中变化
- `IsExperimentalVersion: true`，尚未毕业为正式插件
- **推荐使用**：适合需要大规模实例化动画的项目。虽然是实验性的，但功能完整且由 Epic 官方维护。注意关注 UE 版本升级时的兼容性变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AnimToTexture)
- 官方文档：无（DocsURL 为空）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AnimToTexture/Content)（内置 Mannequin 示例）
