import { IsString, IsEnum, IsUUID, IsObject, ValidateNested, IsOptional } from 'class-validator';
import { Type } from 'class-transformer';

export enum NodeKind {
    DOMAIN = 'DOMAIN',
    PLATFORM = 'PLATFORM',
    SYSTEM = 'SYSTEM',
    CONTAINER = 'CONTAINER',
    COMPONENT = 'COMPONENT',
    INFRA_RESOURCE = 'INFRA_RESOURCE'
}

export class MetadataDto {
    @IsUUID()
    id: string;

    @IsString()
    slug: string;

    @IsString()
    name: string;

    @IsObject()
    @IsOptional()
    labels?: Record<string, string>;

    @IsObject()
    @IsOptional()
    identity_aliases?: Record<string, string[]>;
}

export class CreateNodeDto {
    @IsEnum(NodeKind)
    kind: NodeKind;

    @ValidateNested()
    @Type(() => MetadataDto)
    metadata: MetadataDto;

    @IsObject()
    @IsOptional()
    spec?: any;

    @IsObject()
    @IsOptional()
    status?: any;

    @IsObject()
    @IsOptional()
    version_context?: any;
}
