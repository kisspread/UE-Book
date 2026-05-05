# LidarPointCloudRuntime 模块文档

`LidarPointCloudRuntime` 是点云插件的核心运行时模块，负责点云数据的存储、查询、渲染和文件IO。

## 核心类

### ULidarPointCloud

**头文件**：`LidarPointCloud.h`

点云资产类，继承自 `UObject` 并实现 `IInterface_CollisionDataProvider`。它是整个插件的核心数据容器，内部通过 `FLidarPointCloudOctree` 管理点数据。

**关键属性**：

| 属性 | 类型 | 说明 |
|---|---|---|
| `MaxCollisionError` | `float` | 碰撞精度（cm），越低越精确但构建越慢 |
| `NormalsQuality` | `int32` | 法线计算质量（1-100） |
| `NormalsNoiseTolerance` | `float` | 法线噪声容差 |
| `OriginalCoordinates` | `FVector` | 原始坐标偏移 |
| `LocationOffset` | `FVector` | 渲染时的位置偏移 |
| `Octree` | `FLidarPointCloudOctree` | 八叉树数据结构 |

**关键蓝图函数**：

- **查询**：`GetNumPoints`, `GetNumVisiblePoints`, `GetNumLODs`, `GetBounds`, `GetDataSize`, `GetEstimatedPointSpacing`
- **空间查询**：`HasPointsInSphere/Box`, `HasPointsByRay`, `GetPointsAsCopies`, `GetPointsInSphere/BoxAsCopies`
- **射线检测**：`LineTraceSingle`, `LineTraceMulti`
- **可见性**：`SetVisibilityOfPointsInSphere/Box`, `SetVisibilityOfFirstPointByRay`, `SetVisibilityOfPointsByRay`, `HideAll`, `UnhideAll`, `MarkPointVisibilityDirty`
- **颜色**：`ApplyColorToAllPoints`, `ApplyColorToPointsInSphere/Box`, `ApplyColorToFirstPointByRay`, `ApplyColorToPointsByRay`
- **数据操作**：`InsertPoint`, `InsertPoints`, `RemovePoint`, `RemovePointsInSphere/Box`, `RemoveFirstPointByRay`, `RemovePointsByRay`, `RemoveHiddenPoints`, `SetData`, `Merge`, `MergeSingle`
- **碰撞**：`BuildCollision`, `BuildCollisionWithCallback` (Latent), `RemoveCollision`, `HasCollisionData`, `GetColliderPolys`
- **法线**：`CalculateNormals` (Latent)
- **坐标**：`CenterPoints`, `SetLocationOffset`, `RestoreOriginalCoordinates`, `IsCentered`
- **IO**：`Reimport` (Latent), `Export`, `SetSourcePath`
- **其他**：`Initialize`, `RefreshBounds`, `RefreshRendering`, `IsFullyLoaded`, `LoadAllNodes`, `SetOptimizedForDynamicData`, `SetOptimalCollisionError`

**静态函数**：

- `CreateFromFile` — 从文件创建点云
- `CreateFromData` — 从点数据创建点云
- `AlignClouds` — 对齐多个点云
- `CalculateBoundsFromPoints` — 计算点集包围盒

### FLidarPointCloudPoint

**头文件**：`LidarPointCloudShared.h`

单个点的数据结构，`#pragma pack(1)` 紧凑存储。

| 字段 | 类型 | 说明 |
|---|---|---|
| `Location` | `FVector3f` | 3D 位置 |
| `Color` | `FColor` | RGBA 颜色 |
| `Normal` | `FLidarPointCloudNormal` | 法线（3字节压缩） |
| `bVisible` | `uint8:1` | 是否可见 |
| `ClassificationID` | `uint8:5` | 分类 ID（0-31，对应 LAS 标准分类） |
| `bSelected` | `uint8:1` | 编辑器选择状态 |

**构造函数支持多种参数组合**：
- `(X, Y, Z)` — 仅位置
- `(X, Y, Z, Intensity)` — 位置 + 强度（存入 Alpha）
- `(X, Y, Z, R, G, B, A)` — 位置 + 颜色
- `(X, Y, Z, R, G, B, A, NX, NY, NZ)` — 位置 + 颜色 + 法线
- `(Location, Color, bVisible, ClassificationID)` — 完整参数

### FLidarPointCloudNormal

法线的压缩表示，每分量 1 字节（`uint8`），精度约为 0.8%。

- `SetFromVector(FVector3f)` / `SetFromFloats(X, Y, Z)` — 设置法线
- `ToVector()` — 转换回 `FVector3f`
- `IsValid()` — 检查是否有效（非默认值 127,127,127）

### ULidarPointCloudComponent

**头文件**：`LidarPointCloudComponent.h`

场景组件，继承自 `UMeshComponent`，用于在场景中渲染点云。标记为 `BlueprintSpawnableComponent`。

**外观属性**：

| 属性 | 类型 | 说明 |
|---|---|---|
| `PointSize` | `float` | 点大小，0 表示 1 像素点 |
| `ScalingMethod` | `ELidarPointCloudScalingMethod` | 缩放方式 |
| `GapFillingStrength` | `float` | 间隙填充强度 |
| `ColorSource` | `ELidarPointCloudColorationMode` | 颜色来源 |
| `PointOrientation` | `ELidarPointCloudSpriteOrientation` | 点朝向 |
| `PointSizeBias` | `float` | 点大小偏移（0.035-0.05 效果最佳） |
| `ClassificationColors` | `TMap<int32, FLinearColor>` | 分类颜色映射 |

**颜色调整属性**（Color Adjustment）：

| 属性 | 说明 |
|---|---|
| `Saturation` | 饱和度（0-2） |
| `Contrast` | 对比度（0-2） |
| `Gamma` | Gamma 值（0-2） |
| `Gain` | 增益/发光强度（0-1） |
| `Offset` | 偏移（-1 到 1） |
| `ColorTint` | 色调 |
| `IntensityInfluence` | 强度数据影响度（0-1） |

**渲染属性**：

| 属性 | 说明 |
|---|---|
| `bUseFrustumCulling` | 是否启用视锥裁剪 |
| `MinDepth` / `MaxDepth` | 最小/最大渲染深度 |
| `bDrawNodeBounds` | 是否绘制节点包围盒（调试用） |
| `CustomMaterial` | 自定义材质 |

**缩放方式枚举 `ELidarPointCloudScalingMethod`**：

| 值 | 说明 |
|---|---|
| `PerNode` | 按节点密度缩放（适合密度变化大的数据） |
| `PerNodeAdaptive` | 自适应按节点缩放（推荐，兼顾细节和稳定性） |
| `PerPoint` | 按单点深度缩放（最高细节，但对密度变化敏感） |
| `FixedScreenSize` | 屏幕空间固定大小（PointSize 作为屏幕百分比） |

**颜色模式枚举 `ELidarPointCloudColorationMode`**：

| 值 | 说明 |
|---|---|
| `None` | 仅使用 ColorTint |
| `Data` | 使用导入的 RGB/Intensity 数据 |
| `DataWithClassificationAlpha` | RGB + 分类颜色的 Alpha |
| `Elevation` | 基于高度的颜色渐变 |
| `Position` | 基于相对位置的颜色 |
| `Classification` | 基于分类 ID 的颜色 |

组件提供了与 `ULidarPointCloud` 几乎相同的空间查询和操作函数，但会自动将世界坐标转换为点云本地坐标。

### ALidarPointCloudActor

**头文件**：`LidarPointCloudActor.h`

简单的 Actor 包装器，内含一个 `ULidarPointCloudComponent`。

- `GetPointCloudComponent()` — 获取组件
- `GetPointCloud()` / `SetPointCloud()` — 获取/设置点云资产（蓝图可用）

### ALidarClippingVolume

**头文件**：`LidarPointCloud.h`（末尾定义）

继承自 `AVolume`，用于在指定区域内裁剪点云显示。

| 属性 | 说明 |
|---|---|
| `bEnabled` | 是否启用 |
| `Mode` | `ClipInside`（隐藏内部点）或 `ClipOutside`（隐藏外部点） |
| `Priority` | 处理优先级（高优先级覆盖低优先级） |

## 数据结构

### FLidarPointCloudOctree

**头文件**：`LidarPointCloudOctree.h`

八叉树核心类，管理点云数据的层级存储。

**关键特性**：
- 多级 LOD 支持，按需流式加载节点数据
- 线程安全的数据锁（`DataLock`, `DataReleaseLock`）
- 支持碰撞网格数据
- BulkData 序列化支持
- 遍历八叉树（TraversalOctree）用于渲染

**关键方法**：
- `GetNumPoints/VisiblePoints/Nodes/LODs` — 统计查询
- `GetBounds` / `RefreshBounds` — 包围盒
- `GetPoints/InSphere/InBox/InConvexVolume` — 区域查询
- `RaycastSingle/Multi` — 射线检测
- `SetVisibilityOf...` — 可见性控制
- `ExecuteActionOn...` — 在点上执行操作
- `ApplyColorTo...` — 颜色修改
- `BuildCollision/RemoveCollision` — 碰撞管理
- `InsertPoints` / `RemovePoints` / `RemovePoint` — 数据增删
- `MarkPointVisibilityDirty` / `MarkRenderDataDirty` — 标记脏数据

### FLidarPointCloudOctreeNode

单个八叉树节点，包含：
- 子节点数组（8个子节点，按 XYZ 排列）
- 点数据数组（`TArray<FLidarPointCloudPoint>`，可为流式加载状态）
- BulkData 偏移和大小（用于异步读取）
- 渲染数据缓存（`DataCache`, `VertexFactory`, `RayTracingGeometry`）
- 可见点计数、选择状态

### FLidarPointCloudRay

用于射线检测的射线结构体，使用高效的 Ray-Box 交叉算法（Amy Williams et al. 2004）。

## LOD 管理

### FLidarPointCloudLODManager

**头文件**：`LidarPointCloudLODManager.h`

全局单例（`FTickableGameObject`），每帧 Tick 负责：
1. 收集所有注册的点云组件信息
2. 根据视口参数计算点预算
3. 选择最优节点集合（在预算内最大化视觉质量）
4. 将数据传递给渲染线程

**关键机制**：
- 全局点预算分配，支持多视口
- 可选优先活跃视口（`bPrioritizeActiveViewport`）
- 裁剪体积（Clipping Volume）集成
- 节点生命周期管理（`CachedNodeLifetime`）

### FLidarPointCloudViewData

存储视图信息用于 LOD 计算：
- `ViewOrigin`, `ViewDirection` — 视图位置和方向
- `ScreenSizeFactor` — 屏幕大小因子
- `ViewFrustum` — 视锥体
- `bPIE`, `bHasFocus` — PIE 和焦点状态

## 渲染系统

### 渲染架构

渲染通过 Scene Proxy 模式实现：
- `FLidarPointCloudSceneProxyWrapper` — LOD Manager 与 Scene Proxy 的弱引用桥梁
- `ILidarPointCloudSceneProxy` — Scene Proxy 接口，提供 `UpdateRenderData` 方法
- `FLidarPointCloudProxyUpdateData` — 传递给渲染线程的数据包，包含选中节点列表、裁剪体积、渲染参数

### 渲染缓冲

**头文件**：`Rendering/LidarPointCloudRenderBuffers.h`, `Rendering/LidarPointCloudRendering.h`

- `FLidarPointCloudRenderBuffer` — 点云渲染缓冲
- `FLidarPointCloudVertexFactory` — 顶点工厂
- `FLidarPointCloudRayTracingGeometry` — 光追几何体

## 网格化系统

### LidarPointCloudMeshing 命名空间

**头文件**：`Meshing/LidarPointCloudMeshing.h`

提供从点云生成网格的功能：

- `CalculateNormals()` — 计算法线（多线程）
- `BuildCollisionMesh()` — 构建碰撞三角网格
- `BuildStaticMeshBuffers()` — 构建静态网格缓冲（用于导出 Static Mesh）

**数据结构**：
- `FVertexData` — 顶点数据（Position + Normal + Color）
- `FMeshBuffers` — 网格缓冲（Indices + Vertices + Bounds）

## 文件 IO 系统

### ULidarPointCloudFileIO

**头文件**：`IO/LidarPointCloudFileIO.h`

文件IO管理器（也继承自 `UExporter`），维护一个 Handler 注册表。

**关键静态方法**：
- `Import()` / `Export()` — 导入/导出
- `GetImportSettings()` — 获取导入设置
- `GetSupportedImportExtensions()` / `GetSupportedExportExtensions()` — 获取支持的格式
- `RegisterHandler()` — 注册新的文件处理器
- `FileSupportsConcurrentInsertion()` — 查询是否支持并发插入

### FLidarPointCloudImportResults

导入结果结构体，支持渐进式导入：
- `Points` — 导入的点数据
- `Bounds` — 包围盒
- `OriginalCoordinates` — 原始坐标
- `ClassificationsImported` — 导入的分类ID列表
- 支持进度回调和取消机制

### 格式处理器

| 类 | 格式 | 导入 | 导出 | 并发插入 |
|---|---|---|---|---|
| `ULidarPointCloudFileIO_LAS` | LAS/LAZ | ✅ | ✅ | ✅（LAS） |
| `ULidarPointCloudFileIO_E57` | E57 | ✅ | ❌ | ❌ |
| `ULidarPointCloudFileIO_ASCII` | TXT/XYZ/PTS | ✅ | ✅ | ❌ |

**ASCII 格式特有功能**（`FLidarPointCloudImportSettings_ASCII`）：
- 自动检测文件头（分隔符、列数）
- 可配置列映射（位置XYZ、RGB、强度、法线XYZ）
- 支持 RGB 范围设置
- 编辑器中显示导入 UI

## 枚举类型汇总

| 枚举 | 说明 |
|---|---|
| `ELidarPointCloudAsyncMode` | 异步操作状态（Success / Failure / Progress） |
| `ELidarPointCloudScalingMethod` | 点缩放方式（PerNode / PerNodeAdaptive / PerPoint / FixedScreenSize） |
| `ELidarPointCloudColorationMode` | 颜色模式（None / Data / DataWithClassificationAlpha / Elevation / Position / Classification） |
| `ELidarPointCloudSpriteShape` | 点形状（Square / Circle） |
| `ELidarPointCloudSpriteOrientation` | 点朝向（PreferFacingCamera / PreferFacingNormal） |
| `ELidarPointCloudDuplicateHandling` | 重复点处理（Ignore / SelectFirst / SelectBrighter） |
| `ELidarClippingVolumeMode` | 裁剪模式（ClipInside / ClipOutside） |

## 蓝图函数库

### ULidarPointCloudBlueprintLibrary

**头文件**：`LidarPointCloud.h`

提供全局蓝图节点，使用 `WorldContextObject` 自动查找场景中的点云：

- **创建**：`CreatePointCloudEmpty`, `CreatePointCloudFromFile` (Latent), `CreatePointCloudFromData` (Latent)
- **导出**：`ExportPointCloudToFile`
- **对齐**：`AlignClouds`
- **空间查询**：`ArePointsInSphere`, `ArePointsInBox`, `ArePointsByRay`, `GetPointsInSphereAsCopies`, `GetPointsInBoxAsCopies`
- **射线检测**：`LineTraceSingle`, `LineTraceMulti` — 自动在场景中搜索所有点云组件
- **可见性**：`SetVisibilityOfPointsInSphere/Box`, `SetVisibilityOfFirstPointByRay`, `SetVisibilityOfPointsByRay`
- **颜色**：`ApplyColorToPointsInSphere/Box`, `ApplyColorToFirstPointByRay`, `ApplyColorToPointsByRay`
- **删除**：`RemovePointsInSphere/Box`, `RemoveFirstPointByRay`, `RemovePointsByRay`
- **法线工具**：`NormalFromVector`, `Conv_LidarPointCloudNormalToVector`, `Conv_VectorToLidarPointCloudNormal`

### FLidarPointCloudTraceHit

射线检测结果结构体（用于全局 `LineTraceSingle/Multi`）：

| 字段 | 类型 | 说明 |
|---|---|---|
| `Actor` | `ALidarPointCloudActor*` | 命中的 Actor |
| `Component` | `ULidarPointCloudComponent*` | 命中的组件 |
| `Points` | `TArray<FLidarPointCloudPoint>` | 命中的点 |
