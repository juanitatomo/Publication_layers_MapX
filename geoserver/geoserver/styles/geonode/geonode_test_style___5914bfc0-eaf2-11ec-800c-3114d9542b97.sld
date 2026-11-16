<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<StyledLayerDescriptor version="1.0.0" xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd" xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NamedLayer>
    <Name>test style</Name>
    <UserStyle>
      <Name>test style</Name>
      <Title>test style</Title>
      <FeatureTypeStyle>
        <Rule>
          <Name>&gt;= 1 and &lt; 23</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThanOrEqualTo>
                <PropertyName>COD_PROV</PropertyName>
                <Literal>1</Literal>
              </PropertyIsGreaterThanOrEqualTo>
              <PropertyIsLessThan>
                <PropertyName>COD_PROV</PropertyName>
                <Literal>23</Literal>
              </PropertyIsLessThan>
            </And>
          </Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#7f0000</CssParameter>
              <CssParameter name="fill-opacity">1</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#777777</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>&gt;= 23 and &lt; 45</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThanOrEqualTo>
                <PropertyName>COD_PROV</PropertyName>
                <Literal>23</Literal>
              </PropertyIsGreaterThanOrEqualTo>
              <PropertyIsLessThan>
                <PropertyName>COD_PROV</PropertyName>
                <Literal>45</Literal>
              </PropertyIsLessThan>
            </And>
          </Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#d7301f</CssParameter>
              <CssParameter name="fill-opacity">1</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#777777</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>&gt;= 45 and &lt; 67</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThanOrEqualTo>
                <PropertyName>COD_PROV</PropertyName>
                <Literal>45</Literal>
              </PropertyIsGreaterThanOrEqualTo>
              <PropertyIsLessThan>
                <PropertyName>COD_PROV</PropertyName>
                <Literal>67</Literal>
              </PropertyIsLessThan>
            </And>
          </Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#fc8d59</CssParameter>
              <CssParameter name="fill-opacity">1</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#777777</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>&gt;= 67 and &lt; 89</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThanOrEqualTo>
                <PropertyName>COD_PROV</PropertyName>
                <Literal>67</Literal>
              </PropertyIsGreaterThanOrEqualTo>
              <PropertyIsLessThan>
                <PropertyName>COD_PROV</PropertyName>
                <Literal>89</Literal>
              </PropertyIsLessThan>
            </And>
          </Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#fdd49e</CssParameter>
              <CssParameter name="fill-opacity">1</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#777777</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>&gt;= 89 and &lt;= 111</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThanOrEqualTo>
                <PropertyName>COD_PROV</PropertyName>
                <Literal>89</Literal>
              </PropertyIsGreaterThanOrEqualTo>
              <PropertyIsLessThanOrEqualTo>
                <PropertyName>COD_PROV</PropertyName>
                <Literal>111</Literal>
              </PropertyIsLessThanOrEqualTo>
            </And>
          </Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#fff7ec</CssParameter>
              <CssParameter name="fill-opacity">1</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#777777</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name/>
          <Filter xmlns="http://www.opengis.net/ogc">
            <Or>
              <PropertyIsEqualTo>
                <PropertyName>COD_PROV</PropertyName>
                <Literal>1</Literal>
              </PropertyIsEqualTo>
            </Or>
          </Filter>
          <PointSymbolizer>
            <Graphic>
              <Mark>
                <WellKnownName>circle</WellKnownName>
                <Fill>
                  <CssParameter name="fill">#417505</CssParameter>
                  <CssParameter name="fill-opacity">1</CssParameter>
                </Fill>
                <Stroke>
                  <CssParameter name="stroke">#417505</CssParameter>
                  <CssParameter name="stroke-width">1</CssParameter>
                  <CssParameter name="stroke-opacity">1</CssParameter>
                </Stroke>
              </Mark>
              <Size>10</Size>
            </Graphic>
          </PointSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>